import uuid
from app.core.telemetry import init_run, log, get as get_run
from app.core.registry import load_latest
from app.agents.ingest_csv import IngestCSV
from app.agents.prep_basic import PrepBasic
from app.agents.search_optuna import SearchOptuna
from app.agents.evaluate import Evaluate
from app.agents.deploy_fastapi import DeployFastAPI
import pandas as pd

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
        # Returning a dictionary with a detail message is better for the API
        return {"detail": "no champion yet"}
    return loaded["manifest"]

def predict_rows(rows):
    # Log the received data to check if it's correct
    print(f"Received data for prediction: {rows}")

    loaded = load_latest()
    if not loaded:
        print("ERROR: No champion model found. Returning empty predictions.")
        return {"preds": []}

    try:
        pipe = loaded["pipeline"]
        model = loaded["model"]
        
        # Check if the input is a list of dictionaries as expected
        if not isinstance(rows, list) or not all(isinstance(item, dict) for item in rows):
            print("ERROR: Input 'rows' is not a list of dictionaries.")
            return {"preds": []}

        X = pd.DataFrame(rows)
        print(f"DataFrame created with columns: {X.columns.tolist()}")

        Xp = pipe.transform(X)
        preds = model.predict_proba(Xp)[:,1].tolist()
        
        print(f"Predictions successfully generated: {preds}")
        return {"preds": preds}

    except KeyError as e:
        print(f"ERROR: Missing key in loaded model object: {e}")
        return {"preds": []}
    except Exception as e:
        print(f"ERROR: Failed to run prediction. {e}")
        return {"preds": []}
