"""PQC Evaluation API routes."""
from fastapi import APIRouter
from engines import liboqs_evaluator

router = APIRouter()


@router.get("/run")
async def run_evaluation():
    """Run PQC algorithm evaluation using liboqs."""
    from main import get_pipeline_state
    result = liboqs_evaluator.evaluate_all()
    get_pipeline_state()["evaluation"] = result
    return result


@router.get("/kem")
async def get_kem_results():
    """Get KEM algorithm evaluation results."""
    return {"kem_algorithms": liboqs_evaluator.evaluate_kem_algorithms()}


@router.get("/signatures")
async def get_sig_results():
    """Get signature algorithm evaluation results."""
    return {"signature_algorithms": liboqs_evaluator.evaluate_signature_algorithms()}


@router.get("/classical")
async def get_classical():
    """Get classical algorithm reference data."""
    return {"classical_algorithms": liboqs_evaluator.get_classical_comparison()}


@router.get("/results")
async def get_results():
    """Get cached evaluation results."""
    from main import get_pipeline_state
    state = get_pipeline_state()
    if state["evaluation"]:
        return state["evaluation"]
    return {"message": "No evaluation has been run yet"}
