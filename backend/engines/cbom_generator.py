"""
CBOM (Cryptographic Bill of Materials) Generator.
Aggregates outputs from all pipeline stages into a unified CBOM document.
"""

import json
from datetime import datetime


def generate_cbom(
    discovery_data: dict = None,
    risk_data: dict = None,
    evaluation_data: dict = None,
    benchmark_data: dict = None,
    migration_data: dict = None,
    monitoring_data: dict = None,
    project_name: str = "PQC Crypto Discovery",
) -> dict:
    """Generate comprehensive CBOM from all pipeline phase outputs."""
    
    cbom = {
        "cbom_version": "1.0",
        "metadata": {
            "project_name": project_name,
            "generated_at": datetime.now().isoformat(),
            "tool": "PQC Migration Tool",
            "tool_version": "1.0.0",
            "pipeline_stages_completed": [],
        },
        "algorithm_inventory": [],
        "risk_assessment": {},
        "pqc_evaluation": {},
        "benchmark_results": {},
        "migration_plan": {},
        "monitoring_status": {},
        "summary": {},
    }
    
    # Build algorithm inventory from discovery
    if discovery_data:
        cbom["metadata"]["pipeline_stages_completed"].append("discovery")
        algo_map = {}
        
        for finding in discovery_data.get("findings", []):
            algo = finding.get("algorithm", "Unknown")
            key = algo.upper()
            
            if key not in algo_map:
                algo_map[key] = {
                    "algorithm": algo,
                    "category": finding.get("category", "unknown"),
                    "quantum_vulnerable": finding.get("quantum_vulnerable", False),
                    "locations": [],
                    "pqc_replacement": finding.get("pqc_replacement", ""),
                    "total_occurrences": 0,
                }
            
            algo_map[key]["locations"].append({
                "file": finding.get("file", ""),
                "line": finding.get("line", 0),
                "code_snippet": finding.get("code_snippet", ""),
                "key_size": finding.get("key_size", ""),
            })
            algo_map[key]["total_occurrences"] += 1
        
        cbom["algorithm_inventory"] = list(algo_map.values())
    
    # Add risk assessment
    if risk_data:
        cbom["metadata"]["pipeline_stages_completed"].append("risk_assessment")
        cbom["risk_assessment"] = {
            "overall_risk_score": risk_data.get("overall_risk_score", 0),
            "risk_percentage": risk_data.get("risk_percentage", 0),
            "quantum_vulnerable_count": risk_data.get("quantum_vulnerable_count", 0),
            "severity_breakdown": risk_data.get("severity_breakdown", {}),
            "findings_count": risk_data.get("total", 0),
            "top_risks": risk_data.get("findings", [])[:10],
        }
    
    # Add PQC evaluation
    if evaluation_data:
        cbom["metadata"]["pipeline_stages_completed"].append("pqc_evaluation")
        cbom["pqc_evaluation"] = {
            "tool_used": evaluation_data.get("tool", ""),
            "liboqs_available": evaluation_data.get("liboqs_available", False),
            "kem_algorithms": evaluation_data.get("kem_algorithms", []),
            "signature_algorithms": evaluation_data.get("signature_algorithms", []),
            "recommended_kem": evaluation_data.get("summary", {}).get("fastest_kem"),
            "recommended_sig": evaluation_data.get("summary", {}).get("fastest_sig"),
        }
    
    # Add benchmark results
    if benchmark_data:
        cbom["metadata"]["pipeline_stages_completed"].append("testing")
        cbom["benchmark_results"] = {
            "measured": benchmark_data.get("measured", False),
            "iterations": benchmark_data.get("iterations", 0),
            "kem_benchmarks": benchmark_data.get("kem_benchmarks", []),
            "sig_benchmarks": benchmark_data.get("sig_benchmarks", []),
            "analysis": benchmark_data.get("analysis", {}),
        }
    
    # Add migration plan
    if migration_data:
        cbom["metadata"]["pipeline_stages_completed"].append("migration")
        cbom["migration_plan"] = {
            "total_items": migration_data.get("total_items", 0),
            "items": migration_data.get("migration_items", []),
            "summary": migration_data.get("summary", {}),
            "recommended_approach": migration_data.get("recommended_approach", {}),
        }
    
    # Add monitoring data
    if monitoring_data:
        cbom["metadata"]["pipeline_stages_completed"].append("monitoring")
        cbom["monitoring_status"] = {
            "sonarqube_connected": monitoring_data.get("connected", False),
            "sonarqube_url": monitoring_data.get("url", ""),
            "project_key": monitoring_data.get("project_key", ""),
            "issues": monitoring_data.get("issues", {}),
            "quality_gate": monitoring_data.get("quality_gate", {}),
            "measures": monitoring_data.get("measures", {}),
        }
    
    # Generate summary
    cbom["summary"] = generate_summary(cbom)
    
    return cbom


def generate_summary(cbom: dict) -> dict:
    """Generate CBOM executive summary."""
    inventory = cbom.get("algorithm_inventory", [])
    risk = cbom.get("risk_assessment", {})
    migration = cbom.get("migration_plan", {})
    
    total_algorithms = len(inventory)
    quantum_vulnerable = sum(1 for a in inventory if a.get("quantum_vulnerable"))
    total_locations = sum(a.get("total_occurrences", 0) for a in inventory)
    
    migration_summary = migration.get("summary", {})
    readiness_score = migration_summary.get("readiness_score", 0)
    
    return {
        "total_algorithms_found": total_algorithms,
        "quantum_vulnerable_algorithms": quantum_vulnerable,
        "total_crypto_locations": total_locations,
        "overall_risk_percentage": risk.get("risk_percentage", 0),
        "severity_breakdown": risk.get("severity_breakdown", {}),
        "migration_readiness_score": readiness_score,
        "migration_readiness_label": migration_summary.get("readiness_label", "NOT ASSESSED"),
        "critical_actions_needed": migration_summary.get("critical_migrations", 0),
        "pipeline_stages_completed": cbom.get("metadata", {}).get("pipeline_stages_completed", []),
        "recommendation": get_executive_recommendation(quantum_vulnerable, readiness_score),
    }


def get_executive_recommendation(quantum_vulnerable: int, readiness_score: int) -> str:
    """Generate executive-level recommendation."""
    if quantum_vulnerable == 0:
        return "No quantum-vulnerable cryptographic algorithms detected. Continue monitoring as PQC standards evolve."
    
    if readiness_score < 25:
        return (
            f"CRITICAL: {quantum_vulnerable} quantum-vulnerable algorithms found. "
            "Immediate migration planning required. Begin with hybrid cryptographic approach — "
            "combine classical algorithms with ML-KEM (Kyber) for key exchange and ML-DSA (Dilithium) "
            "for digital signatures. Follow NIST CNSA 2.0 timeline."
        )
    elif readiness_score < 50:
        return (
            f"HIGH RISK: {quantum_vulnerable} quantum-vulnerable algorithms found. "
            "Plan migration within 12-24 months. Adopt crypto-agility practices and begin "
            "hybrid PQC integration in non-production environments."
        )
    elif readiness_score < 75:
        return (
            f"MODERATE: {quantum_vulnerable} algorithms require attention. "
            "Schedule PQC migration as part of regular security updates. "
            "Focus on high-severity items first."
        )
    else:
        return (
            f"LOW RISK: {quantum_vulnerable} minor items found. "
            "Code is mostly quantum-ready. Track remaining items for future migration."
        )


def export_cbom_json(cbom: dict, output_path: str = None) -> str:
    """Export CBOM as formatted JSON."""
    json_str = json.dumps(cbom, indent=2, default=str)
    
    if output_path:
        with open(output_path, "w") as f:
            f.write(json_str)
    
    return json_str


def export_cbom_markdown(cbom: dict) -> str:
    """Export CBOM as human-readable markdown report."""
    summary = cbom.get("summary", {})
    inventory = cbom.get("algorithm_inventory", [])
    risk = cbom.get("risk_assessment", {})
    migration = cbom.get("migration_plan", {})
    
    md = f"""# Cryptographic Bill of Materials (CBOM)
## {cbom.get('metadata', {}).get('project_name', 'Project')}

**Generated:** {cbom.get('metadata', {}).get('generated_at', '')}  
**Tool:** PQC Migration Tool v1.0.0  
**Pipeline Stages:** {', '.join(cbom.get('metadata', {}).get('pipeline_stages_completed', []))}

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Algorithms Found | {summary.get('total_algorithms_found', 0)} |
| Quantum-Vulnerable | {summary.get('quantum_vulnerable_algorithms', 0)} |
| Total Crypto Locations | {summary.get('total_crypto_locations', 0)} |
| Risk Percentage | {summary.get('overall_risk_percentage', 0)}% |
| Migration Readiness | {summary.get('migration_readiness_label', 'N/A')} ({summary.get('migration_readiness_score', 0)}/100) |
| Critical Actions Needed | {summary.get('critical_actions_needed', 0)} |

**Recommendation:** {summary.get('recommendation', '')}

---

## Algorithm Inventory

| Algorithm | Category | Quantum Vulnerable | Occurrences | PQC Replacement |
|-----------|----------|-------------------|-------------|-----------------|
"""
    
    for algo in inventory:
        vuln = "⚠️ YES" if algo.get("quantum_vulnerable") else "✅ No"
        md += f"| {algo['algorithm']} | {algo['category']} | {vuln} | {algo['total_occurrences']} | {algo.get('pqc_replacement', 'N/A')} |\n"
    
    # Risk section
    severity = risk.get("severity_breakdown", {})
    if severity:
        md += f"""
---

## Risk Assessment

| Severity | Count |
|----------|-------|
| 🔴 Critical | {severity.get('critical', 0)} |
| 🟠 High | {severity.get('high', 0)} |
| 🟡 Medium | {severity.get('medium', 0)} |
| 🟢 Low | {severity.get('low', 0)} |
"""
    
    # Migration section
    if migration.get("items"):
        md += "\n---\n\n## Migration Plan\n\n"
        for i, item in enumerate(migration.get("items", [])[:10], 1):
            md += f"### {i}. {item.get('current_algorithm', 'Unknown')} ({item.get('severity', '')})\n"
            md += f"- **File:** {item.get('file', '')}:{item.get('line', '')}\n"
            md += f"- **Replace with:** {item.get('recommended_replacement', '')}\n"
            md += f"- **Effort:** {item.get('migration_effort', '')}\n"
            md += f"- **Timeline:** {item.get('timeline', '')}\n\n"
    
    md += f"\n---\n\n*Generated by PQC Migration Tool — {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n"
    
    return md
