"""Monitoring API routes — SonarQube integration."""
from fastapi import APIRouter
from engines import sonarqube_monitor

router = APIRouter()


@router.get("/status")
async def check_sonarqube():
    """Check SonarQube connection status."""
    return await sonarqube_monitor.check_connection()


@router.get("/report")
async def get_report(project_key: str = "pqc-crypto-discovery"):
    """Get full monitoring report from SonarQube."""
    from main import get_pipeline_state
    result = await sonarqube_monitor.get_full_monitoring_report(project_key)
    get_pipeline_state()["monitoring"] = result
    return result


@router.get("/issues")
async def get_issues(project_key: str = "pqc-crypto-discovery"):
    """Get project issues from SonarQube."""
    return await sonarqube_monitor.get_project_issues(project_key)


@router.get("/quality-gate")
async def get_quality_gate(project_key: str = "pqc-crypto-discovery"):
    """Get quality gate status."""
    return await sonarqube_monitor.get_quality_gate(project_key)


@router.get("/results")
async def get_results():
    """Get cached monitoring results."""
    from main import get_pipeline_state
    state = get_pipeline_state()
    if state["monitoring"]:
        return state["monitoring"]
    return {"message": "No monitoring data available yet"}
