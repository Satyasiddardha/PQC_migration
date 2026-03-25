"""
Migration advisor engine.
Maps classical crypto findings to PQC replacements with actionable migration plans.
"""

import json
import os
import sys
from datetime import datetime

# Prevent relative import issues
from .threat_intel_feed import threat_feed

MIGRATION_MAP_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "migration_map.json")


def load_migration_map() -> list:
    """Load classical-to-PQC migration mapping."""
    try:
        with open(MIGRATION_MAP_PATH, "r") as f:
            data = json.load(f)
            return data.get("mappings", [])
    except Exception:
        return []


def apply_mosca_theorem(algo: str, effort: str) -> dict:
    """
    Apply Mosca's Theorem:
    If M + O >= C (for confidentiality) or M + S >= C (for authentication), enforce immediate migration.
    M = Migration Time (years)
    O = Shelf-life / Data Security Time (years)
    S = System Lifespan (years)
    C = Collapse Time / Q-Day (years until quantum break)
    """
    m = 2.0
    o = 15.0  
    s = 10.0  
    
    # Dynamically fetch Collapse Time (Q-Day) from Threat Intelligence Engine
    c = threat_feed.get_dynamic_collapse_time(algo)
        
    is_at_risk = (m + o) >= c or (m + s) >= c
    
    return {
        "m_years": m,
        "o_years": o,
        "s_years": s,
        "c_years": c,
        "is_at_risk": is_at_risk,
        "mosca_formula": f"M({m}) + max(O({o}), S({s})) >= C({c})",
        "recommendation": "IMMEDIATE MIGRATION REQUIRED" if is_at_risk else "Monitor (Safe margin)"
    }


def generate_migration_plan(discovery_findings: list, evaluation_data: dict = None) -> dict:
    """Generate a migration plan based on discovery findings and PQC evaluation."""
    migration_map = load_migration_map()
    migration_items = []
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    
    for finding in discovery_findings:
        algo = finding.get("algorithm", "").upper()
        key_size = finding.get("key_size", "")
        
        # Find matching migration rule
        rule = find_migration_rule(algo, key_size, migration_map)
        
        if rule:
            effort = rule.get("effort", "MEDIUM")
            mosca = apply_mosca_theorem(algo, effort)
            
            # Mosca Optimization: Override priority if critical
            severity = rule.get("severity", finding.get("severity", "MEDIUM"))
            timeline = rule.get("timeline", "")
            if mosca["is_at_risk"] and severity != "CRITICAL":
                severity = "CRITICAL"
                timeline = f"IMMEDIATE (Mosca's Theorem: M+O >= C -> {mosca['mosca_formula']})"
                
            migration_items.append({
                "finding_id": finding.get("id", ""),
                "file": finding.get("file", ""),
                "line": finding.get("line", 0),
                "current_algorithm": algo,
                "current_key_size": key_size,
                "code_snippet": finding.get("code_snippet", ""),
                "severity": severity,
                "mosca_analysis": mosca,
                "quantum_threat": rule.get("quantum_threat", ""),
                "recommended_replacement": rule.get("pqc_replacement", ""),
                "hybrid_option": rule.get("hybrid_option", ""),
                "migration_effort": effort,
                "nist_security_level": rule.get("nist_level"),
                "timeline": timeline,
                "code_suggestion": generate_code_suggestion(algo, rule, finding),
                "steps": generate_migration_steps(algo, rule),
            })
        else:
            mosca = apply_mosca_theorem(algo, "MEDIUM")
            severity = finding.get("severity", "MEDIUM")
            timeline = "Assess and plan"
            if mosca["is_at_risk"]:
                severity = "CRITICAL"
                timeline = f"IMMEDIATE (Mosca's Theorem: M+O >= C -> {mosca['mosca_formula']})"

            migration_items.append({
                "finding_id": finding.get("id", ""),
                "file": finding.get("file", ""),
                "line": finding.get("line", 0),
                "current_algorithm": algo,
                "severity": severity,
                "mosca_analysis": mosca,
                "quantum_threat": "Potential quantum vulnerability",
                "recommended_replacement": "Evaluate PQC alternatives",
                "migration_effort": "MEDIUM",
                "timeline": timeline,
                "code_suggestion": None,
                "steps": ["Assess quantum vulnerability", "Identify PQC replacement", "Plan migration"],
            })
    
    # Sort by priority
    migration_items.sort(key=lambda x: priority_order.get(x.get("severity", "LOW"), 3))
    
    # Calculate summary
    total_effort = sum(
        {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}.get(item.get("migration_effort", "MEDIUM"), 2)
        for item in migration_items
    )
    
    readiness_score = calculate_readiness_score(migration_items)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "total_items": len(migration_items),
        "migration_items": migration_items,
        "summary": {
            "critical_migrations": sum(1 for i in migration_items if i["severity"] == "CRITICAL"),
            "high_priority": sum(1 for i in migration_items if i["severity"] == "HIGH"),
            "medium_priority": sum(1 for i in migration_items if i["severity"] == "MEDIUM"),
            "low_priority": sum(1 for i in migration_items if i["severity"] == "LOW"),
            "total_effort_score": total_effort,
            "readiness_score": readiness_score,
            "readiness_label": get_readiness_label(readiness_score),
        },
        "recommended_approach": generate_approach_recommendation(migration_items),
    }


def find_migration_rule(algo: str, key_size: str, migration_map: list) -> dict:
    """Find the best matching migration rule for an algorithm."""
    # Try exact match with key size first
    for rule in migration_map:
        classical = rule.get("classical", "").upper()
        if key_size and classical == f"{algo}-{key_size.replace('-bit', '').replace(' (assumed)', '')}":
            return rule
    
    # Try algorithm name match
    for rule in migration_map:
        classical = rule.get("classical", "").upper()
        if classical == algo or classical.startswith(algo):
            return rule
    
    # Try partial match
    for rule in migration_map:
        classical = rule.get("classical", "").upper()
        if algo in classical or classical in algo:
            return rule
    
    return None


def generate_code_suggestion(algo: str, rule: dict, finding: dict) -> dict:
    """Generate code replacement suggestion."""
    replacement = rule.get("pqc_replacement", "")
    hybrid = rule.get("hybrid_option", "")
    
    suggestions = {
        "RSA": {
            "before": finding.get("code_snippet", 'KeyPairGenerator.getInstance("RSA")'),
            "after_pqc": f"// PQC Migration: Replace RSA with {replacement}\n"
                        f"// Using OQS-Provider for Java:\n"
                        f"// Security.addProvider(new OQSProvider());\n"
                        f'// KeyPairGenerator keyGen = KeyPairGenerator.getInstance("ML-KEM");',
            "after_hybrid": f"// Hybrid Migration: Use {hybrid}\n"
                           f"// Combine classical RSA with PQC KEM for transitional period\n"
                           f"// Step 1: Generate RSA keypair (existing)\n"
                           f"// Step 2: Generate ML-KEM keypair (new)\n"
                           f"// Step 3: Combine shared secrets from both",
            "library": "oqs-provider (Java) or liboqs",
        },
        "ECC": {
            "before": finding.get("code_snippet", 'KeyPairGenerator.getInstance("EC")'),
            "after_pqc": f"// PQC Migration: Replace ECC with {replacement}\n"
                        f'// KeyPairGenerator keyGen = KeyPairGenerator.getInstance("ML-DSA");\n'
                        f"// For key exchange: use ML-KEM instead of ECDH",
            "after_hybrid": f"// Hybrid: {hybrid}\n"
                           f"// Combine ECDH with ML-KEM for key exchange\n"
                           f"// Combine ECDSA with ML-DSA for signatures",
            "library": "oqs-provider (Java) or liboqs",
        },
        "AES": {
            "before": finding.get("code_snippet", 'Cipher.getInstance("AES/CBC/PKCS5Padding")'),
            "after_pqc": f"// Quantum Mitigation: Upgrade to AES-256\n"
                        f'Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");\n'
                        f"// Use 256-bit keys (Grover-resistant)",
            "after_hybrid": None,
            "library": "Standard JCE (no additional library needed)",
        },
        "SHA-256": {
            "before": finding.get("code_snippet", 'MessageDigest.getInstance("SHA-256")'),
            "after_pqc": f"// Consider upgrading for long-term quantum safety\n"
                        f'MessageDigest digest = MessageDigest.getInstance("SHA-384");\n'
                        f"// Or use SHA-3: MessageDigest.getInstance(\"SHA3-256\")",
            "after_hybrid": None,
            "library": "Standard JCE",
        },
        "MD5": {
            "before": finding.get("code_snippet", 'MessageDigest.getInstance("MD5")'),
            "after_pqc": f"// CRITICAL: Replace MD5 immediately\n"
                        f'MessageDigest digest = MessageDigest.getInstance("SHA3-256");',
            "after_hybrid": None,
            "library": "Standard JCE",
        },
        "SHA-1": {
            "before": finding.get("code_snippet", 'MessageDigest.getInstance("SHA-1")'),
            "after_pqc": f"// CRITICAL: Replace SHA-1 immediately\n"
                        f'MessageDigest digest = MessageDigest.getInstance("SHA3-256");',
            "after_hybrid": None,
            "library": "Standard JCE",
        },
        "DES": {
            "before": finding.get("code_snippet", 'Cipher.getInstance("DES/...")'),
            "after_pqc": f"// CRITICAL: Replace DES with AES-256\n"
                        f'Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");',
            "after_hybrid": None,
            "library": "Standard JCE",
        },
    }
    
    return suggestions.get(algo, {
        "before": finding.get("code_snippet", ""),
        "after_pqc": f"// Replace with {replacement}",
        "after_hybrid": f"// Consider hybrid: {hybrid}" if hybrid else None,
        "library": "Consult PQC library documentation",
    })


def generate_migration_steps(algo: str, rule: dict) -> list:
    """Generate step-by-step migration instructions."""
    base_steps = [
        f"1. Inventory all {algo} usage locations in your codebase",
        f"2. Assess impact: {rule.get('quantum_threat', 'evaluate quantum risk')}",
    ]
    
    effort = rule.get("effort", "MEDIUM")
    replacement = rule.get("pqc_replacement", "PQC alternative")
    hybrid = rule.get("hybrid_option", "")
    
    if effort in ("HIGH",):
        base_steps.extend([
            f"3. Set up test environment with {replacement}",
            f"4. Implement hybrid approach first: {hybrid}" if hybrid else "4. Plan phased migration",
            f"5. Run integration tests with PQC algorithms",
            f"6. Benchmark performance impact using liboqs",
            f"7. Deploy hybrid mode to staging",
            f"8. Monitor and validate",
            f"9. Transition from hybrid to pure PQC when ecosystem is ready",
        ])
    elif effort in ("MEDIUM",):
        base_steps.extend([
            f"3. Replace with {replacement}",
            f"4. Update configuration and dependencies",
            f"5. Run tests to validate",
            f"6. Deploy and monitor",
        ])
    else:
        base_steps.extend([
            f"3. Replace with {replacement}",
            f"4. Validate and deploy",
        ])
    
    return base_steps


def calculate_readiness_score(items: list) -> int:
    """Calculate PQC migration readiness score (0-100)."""
    if not items:
        return 100
    
    severity_deductions = {"CRITICAL": 25, "HIGH": 15, "MEDIUM": 5, "LOW": 2}
    total_deduction = sum(severity_deductions.get(i.get("severity", "LOW"), 0) for i in items)
    
    return max(0, min(100, 100 - total_deduction))


def get_readiness_label(score: int) -> str:
    """Get human-readable readiness label."""
    if score >= 90:
        return "QUANTUM READY"
    elif score >= 70:
        return "MOSTLY READY - Minor migrations needed"
    elif score >= 50:
        return "PARTIALLY READY - Significant migrations required"
    elif score >= 25:
        return "AT RISK - Major migration effort needed"
    else:
        return "CRITICAL RISK - Immediate action required"


def generate_approach_recommendation(items: list) -> dict:
    """Generate overall migration approach recommendation."""
    critical = sum(1 for i in items if i["severity"] == "CRITICAL")
    high = sum(1 for i in items if i["severity"] == "HIGH")
    
    if critical > 0:
        phase = "IMMEDIATE"
        approach = "Start with critical findings (MD5, DES, SHA-1). These are broken even classically."
    elif high > 0:
        phase = "SHORT-TERM"
        approach = "Plan hybrid migration for RSA/ECC within 12-24 months. Quantum computers capable of breaking these are expected by 2030-2035."
    else:
        phase = "LONG-TERM"
        approach = "Current cryptography is adequate but should be tracked. Plan for PQC migration as standards mature."
    
    return {
        "phase": phase,
        "approach": approach,
        "recommended_strategy": "Crypto-Agility — design systems to easily swap algorithms without major refactoring",
        "standards_reference": "Follow NIST SP 800-208 and CNSA 2.0 timeline recommendations",
    }
