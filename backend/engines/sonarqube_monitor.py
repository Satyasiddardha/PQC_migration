"""
SonarQube monitoring integration.
Connects to a running SonarQube instance to track crypto-related issues and quality over time.
"""

import httpx
import os
from datetime import datetime


SONARQUBE_URL = os.environ.get("SONARQUBE_URL", "http://localhost:9000")
DEFAULT_PROJECT_KEY = "pqc-crypto-discovery"
AUTH = ("admin", "Cys@2206392638843")


async def check_connection() -> dict:
    """Check if SonarQube is accessible."""
    try:
        headers = {"Bypass-Tunnel-Reminder": "true"}
        async with httpx.AsyncClient(timeout=10, auth=AUTH, headers=headers) as client:
            resp = await client.get(f"{SONARQUBE_URL}/api/system/status")
            data = resp.json()
            return {
                "connected": data.get("status") == "UP",
                "version": data.get("version", "unknown"),
                "status": data.get("status", "unknown"),
                "url": SONARQUBE_URL,
            }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
            "url": SONARQUBE_URL,
        }


async def get_project_issues(project_key: str = DEFAULT_PROJECT_KEY) -> dict:
    """Fetch project issues from SonarQube."""
    try:
        headers = {"Bypass-Tunnel-Reminder": "true"}
        async with httpx.AsyncClient(timeout=15, auth=AUTH, headers=headers) as client:
            # Get issues
            resp = await client.get(
                f"{SONARQUBE_URL}/api/issues/search",
                params={
                    "componentKeys": project_key,
                    "ps": 500,
                    "resolved": "false",
                },
            )
            
            if resp.status_code == 200:
                data = resp.json()
                issues = data.get("issues", [])
                
                # Filter and classify crypto-related issues
                crypto_issues = []
                other_issues = []
                
                crypto_keywords = [
                    "crypto", "cipher", "encrypt", "decrypt", "hash", "digest",
                    "rsa", "aes", "des", "md5", "sha", "ssl", "tls", "certificate",
                    "key", "secret", "password", "token",
                ]
                
                for issue in issues:
                    msg = (issue.get("message", "") + issue.get("rule", "")).lower()
                    is_crypto = any(kw in msg for kw in crypto_keywords)
                    
                    classified = {
                        "key": issue.get("key"),
                        "rule": issue.get("rule"),
                        "severity": issue.get("severity", "MINOR"),
                        "message": issue.get("message", ""),
                        "component": issue.get("component", ""),
                        "line": issue.get("line", 0),
                        "status": issue.get("status", ""),
                        "type": issue.get("type", ""),
                        "effort": issue.get("effort", ""),
                        "creation_date": issue.get("creationDate", ""),
                        "is_crypto_related": is_crypto,
                    }
                    
                    if is_crypto:
                        crypto_issues.append(classified)
                    else:
                        other_issues.append(classified)
                
                return {
                    "tool": "sonarqube",
                    "project_key": project_key,
                    "timestamp": datetime.now().isoformat(),
                    "total_issues": len(issues),
                    "crypto_issues": crypto_issues,
                    "crypto_issue_count": len(crypto_issues),
                    "other_issues": other_issues[:20],  # Limit non-crypto
                    "paging": data.get("paging", {}),
                }
            else:
                return {"error": f"SonarQube API returned {resp.status_code}", "tool": "sonarqube"}
                
    except Exception as e:
        return {"error": str(e), "tool": "sonarqube"}


async def get_quality_gate(project_key: str = DEFAULT_PROJECT_KEY) -> dict:
    """Get quality gate status for the project."""
    try:
        headers = {"Bypass-Tunnel-Reminder": "true"}
        async with httpx.AsyncClient(timeout=10, auth=AUTH, headers=headers) as client:
            resp = await client.get(
                f"{SONARQUBE_URL}/api/qualitygates/project_status",
                params={"projectKey": project_key},
            )
            
            if resp.status_code == 200:
                return {
                    "tool": "sonarqube",
                    "data": resp.json(),
                    "timestamp": datetime.now().isoformat(),
                }
    except Exception:
        pass
    
    return {"tool": "sonarqube", "data": None, "error": "Could not fetch quality gate status"}


async def get_project_measures(project_key: str = DEFAULT_PROJECT_KEY) -> dict:
    """Get project metrics/measures."""
    metrics = [
        "security_rating", "reliability_rating", "vulnerabilities",
        "bugs", "code_smells", "ncloc", "coverage",
        "security_hotspots", "security_hotspots_reviewed",
    ]
    
    try:
        headers = {"Bypass-Tunnel-Reminder": "true"}
        async with httpx.AsyncClient(timeout=10, auth=AUTH, headers=headers) as client:
            resp = await client.get(
                f"{SONARQUBE_URL}/api/measures/component",
                params={
                    "component": project_key,
                    "metricKeys": ",".join(metrics),
                },
            )
            
            if resp.status_code == 200:
                data = resp.json()
                measures = {}
                for m in data.get("component", {}).get("measures", []):
                    measures[m["metric"]] = m.get("value", "N/A")
                
                return {
                    "tool": "sonarqube",
                    "project_key": project_key,
                    "measures": measures,
                    "timestamp": datetime.now().isoformat(),
                }
    except Exception as e:
        return {"error": str(e)}
    
    return {"tool": "sonarqube", "measures": {}}


async def get_scan_history(project_key: str = DEFAULT_PROJECT_KEY) -> dict:
    """Get project analysis history."""
    try:
        headers = {"Bypass-Tunnel-Reminder": "true"}
        async with httpx.AsyncClient(timeout=10, auth=AUTH, headers=headers) as client:
            resp = await client.get(
                f"{SONARQUBE_URL}/api/project_analyses/search",
                params={"project": project_key, "ps": 20},
            )
            
            if resp.status_code == 200:
                data = resp.json()
                analyses = []
                for a in data.get("analyses", []):
                    analyses.append({
                        "key": a.get("key"),
                        "date": a.get("date"),
                        "events": a.get("events", []),
                    })
                
                return {
                    "tool": "sonarqube",
                    "project_key": project_key,
                    "analyses": analyses,
                    "total": len(analyses),
                    "timestamp": datetime.now().isoformat(),
                }
    except Exception as e:
        return {"error": str(e)}
    
    return {"tool": "sonarqube", "analyses": []}


async def get_full_monitoring_report(project_key: str = DEFAULT_PROJECT_KEY) -> dict:
    """Get comprehensive monitoring report from SonarQube."""
    connection = await check_connection()
    
    if not connection.get("connected"):
        return {
            "tool": "sonarqube",
            "connected": False,
            "message": "SonarQube is not running. Start it to enable monitoring.",
            "url": SONARQUBE_URL,
            "timestamp": datetime.now().isoformat(),
        }
    
    issues = await get_project_issues(project_key)
    quality_gate = await get_quality_gate(project_key)
    measures = await get_project_measures(project_key)
    history = await get_scan_history(project_key)
    
    return {
        "tool": "sonarqube",
        "connected": True,
        "sonarqube_version": connection.get("version"),
        "url": SONARQUBE_URL,
        "project_key": project_key,
        "timestamp": datetime.now().isoformat(),
        "issues": issues,
        "quality_gate": quality_gate,
        "measures": measures,
        "scan_history": history,
        "audit_log": [
            {
                "timestamp": datetime.now().isoformat(),
                "action": "monitoring_report_generated",
                "details": f"Full monitoring report for {project_key}",
            }
        ],
    }
