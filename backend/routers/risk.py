"""Risk Assessment API routes."""
from fastapi import APIRouter
from engines import sslyze_scanner, cve_scanner

router = APIRouter()


@router.post("/scan-tls")
async def scan_tls(hostname: str = "example.com", port: int = 443):
    """Scan a TLS endpoint using SSLyze."""
    result = sslyze_scanner.scan_tls_endpoint(hostname, port)
    return result


@router.get("/cve-scan")
async def scan_cves():
    """Run CVE scan for crypto vulnerabilities."""
    result = cve_scanner.run_cve_scan()
    return result


@router.post("/analyze")
async def analyze_risk(hostname: str = "example.com"):
    """Run full risk analysis combining discovery, TLS, and CVE data."""
    from main import get_pipeline_state
    state = get_pipeline_state()
    
    discovery = state.get("discovery", {})
    tls_result = sslyze_scanner.get_demo_tls_result(hostname, 443)
    cve_result = cve_scanner.get_curated_cve_results()
    
    risk_result = cve_scanner.analyze_risk(
        discovery.get("findings", []),
        tls_result.get("findings", []),
        cve_result.get("findings", []),
    )
    
    combined = {
        "tls": tls_result,
        "cve": cve_result,
        "analysis": risk_result,
    }
    state["risk"] = combined
    return combined


@router.get("/results")
async def get_results():
    """Get cached risk assessment results."""
    from main import get_pipeline_state
    state = get_pipeline_state()
    if state["risk"]:
        return state["risk"]
    return {"message": "No risk assessment has been run yet"}
