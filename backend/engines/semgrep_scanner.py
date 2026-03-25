"""
Semgrep-based cryptographic discovery engine.
Runs Semgrep CLI with custom PQC rules to detect classical crypto usage in source code.
"""

import subprocess
import json
import os
import re
from pathlib import Path


RULES_PATH = os.path.join(os.path.dirname(__file__), "..", "rules", "crypto-rules.yaml")

# Fallback regex patterns if Semgrep is not available
FALLBACK_PATTERNS = {
    "RSA": {
        "patterns": [
            r'KeyPairGenerator\.getInstance\(\s*"RSA"\s*\)',
            r'Cipher\.getInstance\(\s*"RSA[^"]*"\s*\)',
            r'RSA\.generate\(',
            r'RSAKeyGenParameterSpec',
            r'new\s+RSAPublicKeySpec',
        ],
        "severity": "HIGH",
        "quantum_vulnerable": True,
        "category": "asymmetric",
        "pqc_replacement": "ML-KEM (Kyber)",
    },
    "ECC": {
        "patterns": [
            r'KeyPairGenerator\.getInstance\(\s*"EC"\s*\)',
            r'KeyPairGenerator\.getInstance\(\s*"ECDSA"\s*\)',
            r'ECDH',
            r'Curve25519',
            r'SECP256',
            r'ECC\.generate\(',
            r'ec\.generate_private_key\(',
        ],
        "severity": "HIGH",
        "quantum_vulnerable": True,
        "category": "asymmetric",
        "pqc_replacement": "ML-KEM (Kyber) + ML-DSA (Dilithium)",
    },
    "AES": {
        "patterns": [
            r'Cipher\.getInstance\(\s*"AES[^"]*"\s*\)',
            r'AES\.new\(',
            r'algorithms\.AES\(',
            r'AESKeyGenParameterSpec',
        ],
        "severity": "MEDIUM",
        "quantum_vulnerable": False,
        "category": "symmetric",
        "pqc_replacement": "AES-256 (increase key size for Grover resistance)",
    },
    "DES": {
        "patterns": [
            r'Cipher\.getInstance\(\s*"DES[^"]*"\s*\)',
            r'DES\.new\(',
            r'DESede',
        ],
        "severity": "CRITICAL",
        "quantum_vulnerable": True,
        "category": "symmetric",
        "pqc_replacement": "AES-256",
    },
    "MD5": {
        "patterns": [
            r'MessageDigest\.getInstance\(\s*"MD5"\s*\)',
            r'hashlib\.md5\(',
            r'MD5\.Create\(',
        ],
        "severity": "CRITICAL",
        "quantum_vulnerable": True,
        "category": "hash",
        "pqc_replacement": "SHA-3",
    },
    "SHA-1": {
        "patterns": [
            r'MessageDigest\.getInstance\(\s*"SHA-1"\s*\)',
            r'hashlib\.sha1\(',
            r'SHA1\.Create\(',
        ],
        "severity": "CRITICAL",
        "quantum_vulnerable": True,
        "category": "hash",
        "pqc_replacement": "SHA-3 or SHA-384",
    },
    "SHA-256": {
        "patterns": [
            r'MessageDigest\.getInstance\(\s*"SHA-256"\s*\)',
            r'hashlib\.sha256\(',
            r'SHA256\.Create\(',
        ],
        "severity": "LOW",
        "quantum_vulnerable": False,
        "category": "hash",
        "pqc_replacement": "SHA-384 or SHA-3 (for long-term quantum safety)",
    },
    "Hardcoded Key": {
        "patterns": [
            r'private\s+static\s+final\s+String\s+\w*(key|secret|password|token)\w*\s*=\s*"[^"]{16,}"',
            r'(api[_-]?key|secret[_-]?key|private[_-]?key)\s*[:=]\s*["\'][^"\']{16,}["\']',
        ],
        "severity": "CRITICAL",
        "quantum_vulnerable": True,
        "category": "secret",
        "pqc_replacement": "Use secure key management (HSM/KMS)",
    },
}

SUPPORTED_EXTENSIONS = {".java", ".py", ".js", ".ts", ".go", ".c", ".cpp", ".cs", ".rb"}


def run_semgrep_scan(target_path: str) -> dict:
    """Run Semgrep CLI and return parsed results."""
    abs_rules = os.path.abspath(RULES_PATH)
    abs_target = os.path.abspath(target_path)
    
    try:
        result = subprocess.run(
            ["semgrep", "--config", abs_rules, "--json", "--no-git-ignore", abs_target],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=os.path.dirname(abs_target),
        )
        
        if result.returncode in (0, 1):  # 0=clean, 1=findings
            output = json.loads(result.stdout)
            return parse_semgrep_output(output)
        else:
            print(f"Semgrep error: {result.stderr}")
            return None
    except FileNotFoundError:
        print("Semgrep not found, using fallback regex scanner")
        return None
    except subprocess.TimeoutExpired:
        print("Semgrep timed out")
        return None
    except Exception as e:
        print(f"Semgrep error: {e}")
        return None


def parse_semgrep_output(output: dict) -> dict:
    """Parse Semgrep JSON output into standardized findings."""
    findings = []
    
    for result in output.get("results", []):
        extra = result.get("extra", {})
        metadata = extra.get("metadata", {})
        
        findings.append({
            "id": result.get("check_id", "unknown"),
            "file": result.get("path", ""),
            "line": result.get("start", {}).get("line", 0),
            "end_line": result.get("end", {}).get("line", 0),
            "column": result.get("start", {}).get("col", 0),
            "code_snippet": extra.get("lines", "").strip(),
            "message": extra.get("message", ""),
            "severity": result.get("extra", {}).get("severity", "WARNING"),
            "algorithm": metadata.get("algorithm", "Unknown"),
            "category": metadata.get("category", "unknown"),
            "quantum_vulnerable": metadata.get("quantum_vulnerable", False),
            "pqc_replacement": metadata.get("pqc_replacement", ""),
            "cwe": metadata.get("cwe", ""),
            "tool": "semgrep",
        })
    
    return {
        "tool": "semgrep",
        "findings": findings,
        "total": len(findings),
        "errors": output.get("errors", []),
    }


def run_fallback_scan(target_path: str) -> dict:
    """Fallback regex-based scanner when Semgrep is unavailable."""
    abs_target = os.path.abspath(target_path)
    findings = []
    finding_id = 0
    
    target = Path(abs_target)
    files = []
    
    if target.is_file():
        files = [target]
    elif target.is_dir():
        for ext in SUPPORTED_EXTENSIONS:
            files.extend(target.rglob(f"*{ext}"))
    
    for file_path in files:
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.split("\n")
            
            for algo_name, config in FALLBACK_PATTERNS.items():
                for pattern in config["patterns"]:
                    for i, line in enumerate(lines, 1):
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        for match in matches:
                            finding_id += 1
                            
                            # Extract key size if present
                            key_size = extract_key_size(line, algo_name)
                            
                            findings.append({
                                "id": f"pqc-{algo_name.lower().replace(' ','-')}-{finding_id}",
                                "file": str(file_path.relative_to(target if target.is_dir() else target.parent)),
                                "line": i,
                                "end_line": i,
                                "column": match.start() + 1,
                                "code_snippet": line.strip(),
                                "message": f"{algo_name} usage detected — {get_threat_description(algo_name)}",
                                "severity": config["severity"],
                                "algorithm": algo_name,
                                "category": config["category"],
                                "quantum_vulnerable": config["quantum_vulnerable"],
                                "pqc_replacement": config["pqc_replacement"],
                                "key_size": key_size,
                                "cwe": "CWE-327",
                                "tool": "regex-scanner",
                            })
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
    
    # Deduplicate by file+line+algorithm
    seen = set()
    unique_findings = []
    for f in findings:
        key = (f["file"], f["line"], f["algorithm"])
        if key not in seen:
            seen.add(key)
            unique_findings.append(f)
    
    return {
        "tool": "regex-scanner",
        "findings": unique_findings,
        "total": len(unique_findings),
        "files_scanned": len(files),
    }


def extract_key_size(line: str, algo: str) -> str:
    """Try to extract key size from the code line."""
    size_match = re.search(r'initialize\(\s*(\d+)', line)
    if size_match:
        return f"{size_match.group(1)}-bit"
    
    if "AES-256" in line or "aes256" in line.lower():
        return "256-bit"
    if "AES-128" in line or "aes128" in line.lower():
        return "128-bit"
    
    # Defaults based on algorithm
    defaults = {
        "RSA": "2048-bit (assumed)",
        "ECC": "256-bit (assumed)",
        "AES": "128/256-bit",
        "DES": "56-bit",
    }
    return defaults.get(algo, "unknown")


def get_threat_description(algo: str) -> str:
    """Get quantum threat description for an algorithm."""
    threats = {
        "RSA": "Vulnerable to Shor's algorithm. A sufficiently powerful quantum computer can factor RSA keys in polynomial time.",
        "ECC": "Vulnerable to Shor's algorithm. Quantum computers can solve the elliptic curve discrete log problem.",
        "AES": "Grover's algorithm halves effective key length. AES-128 → 64-bit security. Use AES-256.",
        "DES": "Already broken classically. Quantum attacks make it trivially breakable.",
        "MD5": "Cryptographically broken (classical collision attacks). Quantum acceleration makes it worse.",
        "SHA-1": "Known collision attacks. Deprecated by NIST. Quantum acceleration increases risk.",
        "SHA-256": "Safe for now. Grover's reduces to ~128-bit security. Consider SHA-384 for long-term.",
        "Hardcoded Key": "Hardcoded secrets are a critical security risk regardless of algorithm.",
    }
    return threats.get(algo, "Potential quantum vulnerability detected.")


def scan(target_path: str) -> dict:
    """Main entry point — tries Semgrep first, falls back to regex scanner."""
    semgrep_result = run_semgrep_scan(target_path)
    
    if semgrep_result and semgrep_result["total"] > 0:
        return semgrep_result
    
    # Always run fallback to catch more patterns
    fallback_result = run_fallback_scan(target_path)
    
    if semgrep_result and semgrep_result["total"] == 0:
        # Semgrep found nothing, use fallback
        return fallback_result
    
    # Merge if both have results
    if semgrep_result:
        merged = semgrep_result.copy()
        existing_keys = {(f["file"], f["line"], f["algorithm"]) for f in merged["findings"]}
        for f in fallback_result["findings"]:
            key = (f["file"], f["line"], f["algorithm"])
            if key not in existing_keys:
                merged["findings"].append(f)
                existing_keys.add(key)
        merged["total"] = len(merged["findings"])
        merged["tool"] = "semgrep+regex"
        return merged
    
    return fallback_result
