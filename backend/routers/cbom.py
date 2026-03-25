"""CBOM API routes."""
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from engines import cbom_generator

router = APIRouter()


@router.post("/generate")
async def generate_cbom():
    """Generate CBOM from all pipeline stage data."""
    from main import get_pipeline_state
    state = get_pipeline_state()
    
    risk_analysis = None
    if state.get("risk"):
        risk_analysis = state["risk"].get("analysis")
    
    cbom = cbom_generator.generate_cbom(
        discovery_data=state.get("discovery"),
        risk_data=risk_analysis,
        evaluation_data=state.get("evaluation"),
        benchmark_data=state.get("testing"),
        migration_data=state.get("migration"),
        monitoring_data=state.get("monitoring"),
    )
    state["cbom"] = cbom
    return cbom


@router.get("/json")
async def get_cbom_json():
    """Get CBOM in JSON format."""
    from main import get_pipeline_state
    state = get_pipeline_state()
    if state["cbom"]:
        return state["cbom"]
    return {"message": "No CBOM has been generated yet. Run the pipeline first."}


@router.get("/markdown", response_class=PlainTextResponse)
async def get_cbom_markdown():
    """Get CBOM in markdown format."""
    from main import get_pipeline_state
    state = get_pipeline_state()
    if state["cbom"]:
        return cbom_generator.export_cbom_markdown(state["cbom"])
    return "No CBOM has been generated yet. Run the pipeline first."


@router.get("/results")
async def get_results():
    """Get cached CBOM data."""
    from main import get_pipeline_state
    state = get_pipeline_state()
    if state["cbom"]:
        return state["cbom"]
    return {"message": "No CBOM has been generated yet"}
