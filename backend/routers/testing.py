"""Testing & Benchmarking API routes."""
from fastapi import APIRouter
from engines import liboqs_benchmark

router = APIRouter()


@router.get("/run")
async def run_benchmarks(iterations: int = 50):
    """Run PQC benchmarks using liboqs."""
    from main import get_pipeline_state
    result = liboqs_benchmark.run_benchmarks(iterations=iterations)
    get_pipeline_state()["testing"] = result
    return result


@router.get("/results")
async def get_results():
    """Get cached benchmark results."""
    from main import get_pipeline_state
    state = get_pipeline_state()
    if state["testing"]:
        return state["testing"]
    return {"message": "No benchmarks have been run yet"}
