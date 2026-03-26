"""
PQC Migration Tool — FastAPI Backend
Main entry point orchestrating all pipeline stages.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import discovery, risk, evaluation, testing, migration, monitoring, cbom, intelligence

app = FastAPI(
    title="PQC Migration Tool",
    description="End-to-end Post-Quantum Cryptography Migration Tool API",
    version="1.0.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(discovery.router, prefix="/api/discovery", tags=["Discovery"])
app.include_router(risk.router, prefix="/api/risk", tags=["Risk Assessment"])
app.include_router(evaluation.router, prefix="/api/evaluation", tags=["PQC Evaluation"])
app.include_router(testing.router, prefix="/api/testing", tags=["Testing & Benchmarks"])
app.include_router(migration.router, prefix="/api/migration", tags=["Migration"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["Monitoring"])
app.include_router(cbom.router, prefix="/api/cbom", tags=["CBOM"])
app.include_router(intelligence.router, prefix="/api/intelligence", tags=["PQC Intelligence Layer"])
# In-memory store for pipeline state
pipeline_state = {
    "discovery": None,
    "risk": None,
    "evaluation": None,
    "testing": None,
    "migration": None,
    "monitoring": None,
    "cbom": None,
}


def get_pipeline_state():
    return pipeline_state


@app.get("/")
async def root():
    return {"message": "PQC Migration Tool API", "version": "1.0.0"}


@app.get("/api/pipeline/status")
async def pipeline_status():
    """Get the status of all pipeline stages."""
    status = {}
    for stage, data in pipeline_state.items():
        status[stage] = {
            "completed": data is not None,
            "has_data": data is not None and bool(data),
        }
    return {"pipeline": status}


@app.post("/api/pipeline/run-all")
async def run_full_pipeline(target_path: str = "../../src"):
    """Run all pipeline stages sequentially."""
    from engines import semgrep_scanner, cve_scanner, sslyze_scanner
    from engines import liboqs_evaluator, liboqs_benchmark
    from engines import migration_advisor, sonarqube_monitor, cbom_generator
    
    # Stage 1: Discovery
    discovery_result = semgrep_scanner.scan(target_path)
    pipeline_state["discovery"] = discovery_result
    
    # Stage 2: Risk Assessment
    tls_result = sslyze_scanner.get_demo_tls_result("example.com", 443)
    cve_result = cve_scanner.get_curated_cve_results()
    risk_result = cve_scanner.analyze_risk(
        discovery_result.get("findings", []),
        tls_result.get("findings", []),
        cve_result.get("findings", []),
    )
    pipeline_state["risk"] = {
        "tls": tls_result,
        "cve": cve_result,
        "analysis": risk_result,
    }
    
    # Stage 3: PQC Evaluation
    eval_result = liboqs_evaluator.evaluate_all()
    pipeline_state["evaluation"] = eval_result
    
    # Stage 4: Testing/Benchmarks
    bench_result = liboqs_benchmark.run_benchmarks(iterations=50)
    pipeline_state["testing"] = bench_result
    
    # Stage 5: Migration
    migration_result = migration_advisor.generate_migration_plan(
        discovery_result.get("findings", []),
        eval_result,
    )
    pipeline_state["migration"] = migration_result
    
    # Stage 6: Monitoring
    monitoring_result = await sonarqube_monitor.get_full_monitoring_report()
    pipeline_state["monitoring"] = monitoring_result
    
    # Stage 7: CBOM
    cbom_result = cbom_generator.generate_cbom(
        discovery_data=discovery_result,
        risk_data=risk_result,
        evaluation_data=eval_result,
        benchmark_data=bench_result,
        migration_data=migration_result,
        monitoring_data=monitoring_result,
    )
    pipeline_state["cbom"] = cbom_result
    
    return {
        "status": "completed",
        "stages_completed": 7,
        "summary": cbom_result.get("summary", {}),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
