"""
CVE scanner using cve-bin-tool for known crypto vulnerabilities.
"""

import subprocess
import json
from datetime import datetime


# Curated crypto CVE database for common libraries
CRYPTO_CVES = [
    {
        "cve_id": "CVE-2023-0286",
        "library": "OpenSSL",
        "severity": "HIGH",
        "cvss": 7.4,
        "description": "X.400 address type confusion in X.509 GeneralName — memory read vulnerability",
        "affected_versions": "OpenSSL < 3.0.8, < 1.1.1t",
        "crypto_relevance": "Certificate parsing vulnerability in TLS implementations",
        "quantum_relevant": False,
    },
    {
        "cve_id": "CVE-2022-4304",
        "library": "OpenSSL",
        "severity": "MEDIUM",
        "cvss": 5.9,
        "description": "RSA decryption timing oracle in PKCS#1 v1.5 — Marvin Attack",
        "affected_versions": "OpenSSL < 3.0.8",
        "crypto_relevance": "Side-channel attack on RSA decryption",
        "quantum_relevant": True,
    },
    {
        "cve_id": "CVE-2023-5678",
        "library": "OpenSSL",
        "severity": "MEDIUM",
        "cvss": 5.3,
        "description": "DH key generation and check excessively slow for large modulus",
        "affected_versions": "OpenSSL < 3.1.4, < 3.0.12",
        "crypto_relevance": "DH key exchange vulnerability — algorithm already quantum-vulnerable",
        "quantum_relevant": True,
    },
    {
        "cve_id": "CVE-2023-46604",
        "library": "Apache Commons",
        "severity": "CRITICAL",
        "cvss": 10.0,
        "description": "Remote code execution via ClassInfo deserialization",
        "affected_versions": "Apache ActiveMQ < 5.15.16, < 5.16.7",
        "crypto_relevance": "Can bypass TLS-protected channels through RCE",
        "quantum_relevant": False,
    },
    {
        "cve_id": "CVE-2022-42898",
        "library": "MIT Kerberos",
        "severity": "HIGH",
        "cvss": 8.8,
        "description": "Integer overflow in PAC parsing — heap buffer overflow",
        "affected_versions": "krb5 < 1.19.4, < 1.20.1",
        "crypto_relevance": "Kerberos uses DES/3DES/AES — authentication protocol vulnerability",
        "quantum_relevant": True,
    },
    {
        "cve_id": "CVE-2024-3094",
        "library": "XZ Utils",
        "severity": "CRITICAL",
        "cvss": 10.0,
        "description": "Supply chain backdoor in liblzma affecting OpenSSH authentication",
        "affected_versions": "xz 5.6.0 - 5.6.1",
        "crypto_relevance": "Backdoor bypasses SSH key authentication — compromises entire crypto chain",
        "quantum_relevant": True,
    },
    {
        "cve_id": "CVE-2023-48795",
        "library": "OpenSSH",
        "severity": "MEDIUM",
        "cvss": 5.9,
        "description": "Terrapin Attack — SSH Binary Packet Protocol prefix truncation",
        "affected_versions": "OpenSSH < 9.6",
        "crypto_relevance": "Downgrade attack on SSH encryption — can force weaker algorithms",
        "quantum_relevant": True,
    },
    {
        "cve_id": "CVE-2021-44228",
        "library": "Log4j",
        "severity": "CRITICAL",
        "cvss": 10.0,
        "description": "Log4Shell — JNDI injection RCE in Java logging framework",
        "affected_versions": "Log4j < 2.15.0",
        "crypto_relevance": "Affects Java applications using cryptographic libraries — can exfiltrate keys",
        "quantum_relevant": False,
    },
]


def run_cve_scan(target_path: str = None) -> dict:
    """Run cve-bin-tool scan on target path."""
    try:
        cmd = ["cve-bin-tool", "--format", "json"]
        if target_path:
            cmd.append(target_path)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        
        if result.stdout:
            cve_data = json.loads(result.stdout)
            return parse_cve_results(cve_data)
    except FileNotFoundError:
        print("cve-bin-tool not found, using curated CVE database")
    except subprocess.TimeoutExpired:
        print("cve-bin-tool timed out")
    except Exception as e:
        print(f"cve-bin-tool error: {e}")
    
    return get_curated_cve_results()


def parse_cve_results(cve_data: dict) -> dict:
    """Parse cve-bin-tool JSON output."""
    findings = []
    
    for item in cve_data if isinstance(cve_data, list) else cve_data.get("results", []):
        findings.append({
            "cve_id": item.get("cve_number", "unknown"),
            "library": item.get("product", "unknown"),
            "severity": item.get("severity", "MEDIUM"),
            "cvss": item.get("score", 0),
            "description": item.get("description", ""),
            "affected_versions": item.get("version", ""),
            "crypto_relevance": "Potential impact on cryptographic operations",
            "quantum_relevant": False,
        })
    
    return {
        "tool": "cve-bin-tool",
        "scan_time": datetime.now().isoformat(),
        "findings": findings,
        "total": len(findings),
    }


def get_curated_cve_results() -> dict:
    """Return curated crypto-relevant CVE database."""
    return {
        "tool": "cve-bin-tool (curated database)",
        "scan_time": datetime.now().isoformat(),
        "findings": CRYPTO_CVES,
        "total": len(CRYPTO_CVES),
        "summary": {
            "critical": sum(1 for c in CRYPTO_CVES if c["severity"] == "CRITICAL"),
            "high": sum(1 for c in CRYPTO_CVES if c["severity"] == "HIGH"),
            "medium": sum(1 for c in CRYPTO_CVES if c["severity"] == "MEDIUM"),
            "quantum_relevant": sum(1 for c in CRYPTO_CVES if c["quantum_relevant"]),
        },
    }


def analyze_risk(discovery_findings: list, tls_findings: list = None, cve_findings: list = None) -> dict:
    """Aggregate all risk assessment data and compute risk scores."""
    all_findings = []
    severity_weights = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}
    
    # Score discovery findings
    for f in discovery_findings:
        risk_score = severity_weights.get(f.get("severity", "LOW"), 1)
        if f.get("quantum_vulnerable"):
            risk_score *= 1.5  # Boost quantum-vulnerable findings
        
        all_findings.append({
            "source": "discovery",
            "id": f.get("id"),
            "severity": f.get("severity", "LOW"),
            "risk_score": round(risk_score, 1),
            "algorithm": f.get("algorithm", "unknown"),
            "file": f.get("file", ""),
            "line": f.get("line", 0),
            "quantum_vulnerable": f.get("quantum_vulnerable", False),
            "description": f.get("message", ""),
            "recommendation": f.get("pqc_replacement", ""),
        })
    
    # Add TLS findings
    if tls_findings:
        for f in tls_findings:
            risk_score = severity_weights.get(f.get("severity", "MEDIUM"), 2)
            if f.get("quantum_relevant"):
                risk_score *= 1.5
            
            all_findings.append({
                "source": "tls",
                "severity": f.get("severity", "MEDIUM"),
                "risk_score": round(risk_score, 1),
                "type": f.get("type", ""),
                "protocol": f.get("protocol", ""),
                "quantum_vulnerable": f.get("quantum_relevant", False),
                "description": f.get("message", ""),
                "recommendation": f.get("recommendation", ""),
            })
    
    # Add CVE findings
    if cve_findings:
        for f in cve_findings:
            risk_score = severity_weights.get(f.get("severity", "MEDIUM"), 2)
            if f.get("quantum_relevant"):
                risk_score *= 1.5
            
            all_findings.append({
                "source": "cve",
                "cve_id": f.get("cve_id", ""),
                "severity": f.get("severity", "MEDIUM"),
                "risk_score": round(risk_score, 1),
                "library": f.get("library", ""),
                "quantum_vulnerable": f.get("quantum_relevant", False),
                "description": f.get("description", ""),
                "cvss": f.get("cvss", 0),
            })
    
    # Sort by risk score descending
    all_findings.sort(key=lambda x: x["risk_score"], reverse=True)
    
    # Compute overall risk metrics
    total_score = sum(f["risk_score"] for f in all_findings)
    max_possible = len(all_findings) * 6  # Max is CRITICAL + quantum = 4 * 1.5 = 6
    risk_percentage = round((total_score / max_possible * 100) if max_possible > 0 else 0, 1)
    
    return {
        "findings": all_findings,
        "total": len(all_findings),
        "overall_risk_score": round(total_score, 1),
        "risk_percentage": risk_percentage,
        "quantum_vulnerable_count": sum(1 for f in all_findings if f.get("quantum_vulnerable")),
        "severity_breakdown": {
            "critical": sum(1 for f in all_findings if f["severity"] == "CRITICAL"),
            "high": sum(1 for f in all_findings if f["severity"] == "HIGH"),
            "medium": sum(1 for f in all_findings if f["severity"] == "MEDIUM"),
            "low": sum(1 for f in all_findings if f["severity"] == "LOW"),
        },
    }
