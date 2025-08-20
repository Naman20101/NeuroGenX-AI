import uuid
from app.core.telemetry import init_run, log, get as get_run
from app.core.registry import load_latest
from ..agents.ingest_csv import IngestCSV
from app.agents.prep_basic import PrepBasic
from app.agents.search_optuna import SearchOptuna
from app.agents.evaluate import Evaluate
from app.agents.deploy_fastapi import DeployFastAPI

def start_run(req: dict):
    run_id = str(uuid.uuid4())[:8]
    init_run(run_id, req)
    ctx = {"run_id": run_id, **req}
    for stage, agent in [
        ("ingest", IngestCSV()),
        ("prep",   PrepBasic()),
        ("search", SearchOptuna()),
        ("eval",   Evaluate()),
        ("deploy", DeployFastAPI()),
    ]:
        ctx = agent.run(ctx)
        log(run_id, stage, {"ok": True, **{k: v for k, v in ctx.items() if k in ("metrics","search_summary")}})
    log(run_id, "done", {"manifest": ctx.get("manifest")})
    return run_id

def get_status(run_id: str):
    return get_run(run_id)

def load_champion():
    loaded = load_latest()
    if not loaded:
        return {"detail": "no champion yet"}
    return loaded["manifest"]

def predict_rows(rows):
    loaded = load_latest()
    if not loaded:
        return []
    pipe = loaded["pipeline"]
    model = loaded["model"]
    import pandas as pd
    X = pd.DataFrame(rows)
    Xp = pipe.transform(X)
    return model.predict_proba(Xp)[:,1].tolist()
