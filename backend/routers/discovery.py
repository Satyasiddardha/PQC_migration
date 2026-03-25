"""Discovery API routes."""
from fastapi import APIRouter
from engines import semgrep_scanner

router = APIRouter()


@router.post("/scan")
async def scan_code(target_path: str = "../../src"):
    """Run crypto discovery scan on the target path."""
    from main import get_pipeline_state
    result = semgrep_scanner.scan(target_path)
    get_pipeline_state()["discovery"] = result
    return result


@router.get("/results")
async def get_results():
    """Get cached discovery results."""
    from main import get_pipeline_state
    state = get_pipeline_state()
    if state["discovery"]:
        return state["discovery"]
    return {"message": "No discovery scan has been run yet", "findings": [], "total": 0}
