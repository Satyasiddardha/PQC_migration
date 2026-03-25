"""Migration API routes."""
from fastapi import APIRouter
from engines import migration_advisor

router = APIRouter()


@router.post("/plan")
async def generate_plan():
    """Generate migration plan from discovery findings."""
    from main import get_pipeline_state
    state = get_pipeline_state()
    
    discovery = state.get("discovery", {})
    evaluation = state.get("evaluation", {})
    
    result = migration_advisor.generate_migration_plan(
        discovery.get("findings", []),
        evaluation,
    )
    state["migration"] = result
    return result


@router.get("/results")
async def get_results():
    """Get cached migration plan."""
    from main import get_pipeline_state
    state = get_pipeline_state()
    if state["migration"]:
        return state["migration"]
    return {"message": "No migration plan has been generated yet"}
