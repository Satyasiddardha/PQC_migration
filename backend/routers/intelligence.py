from fastapi import APIRouter, Body
from typing import Dict, Any
from engines.intelligence_layer import generate_pqc_recommendations

router = APIRouter()

@router.post("/recommendations")
async def get_pqc_recommendations(payload: Dict[str, Any] = Body(...)):
    """
    Accepts a standard CBOM asset list and generates PQC migration recommendations
    based on algorithm type, usage, and risk level.
    """
    return generate_pqc_recommendations(payload)
