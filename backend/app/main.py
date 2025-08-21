from __future__ import annotations
import os, io, threading, traceback
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import orjson
import pandas as pd

from .core.schemas import RunRequest
from .storage import save_dataset, load_csv, new_run, append_event, set_status, get_status, load_champion

# --- THIS IS THE CORRECTED PART ---
# The import path for training needs to include the 'core' directory.
from .core.training import train_genetic

app = FastAPI(title="NeuroGenX NG-1 v2", default_response_class=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True
)

@app.get("/")
def root():
    return {"message": "NeuroGenX API v2 running."}

@app.post("/datasets/upload")
async def upload_dataset(file: UploadFile = File(...)):
    # Save uploaded file to temp then into storage
    contents = await file.read()
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(contents)
    dst = save_dataset(temp_path, file.filename)
    try:
        df = pd.read_csv(dst, nrows=100)  # quick peek
        cols = list(df.columns)
        dtypes = {c: str(df[c].dtype) for c in cols}
    except Exception:
        cols, dtypes = [], {}
    return {"dataset_id": file.filename, "columns": cols, "dtypes": dtypes}

def _background_train(run_id: str, req: RunRequest):
    try:
        df = load_csv(req.dataset_id)
        res = train_genetic(run_id, df, req.target, req.n_trials)
        if not res.get("ok"):
            set_status(run_id, "error")
            append_event(run_id, "error", {"msg": res.get("error", "unknown")})
    except Exception as e:
        set_status(run_id, "error")
        append_event(run_id, "error", {
            "msg": str(e),
            "trace": traceback.format_exc()[:5000]
        })

@app.post("/runs/start")
def runs_start(req: RunRequest):
    run_id = new_run()
    append_event(run_id, "start", req.dict())
    set_status(run_id, "running")
    t = threading.Thread(target=_background_train, args=(run_id, req), daemon=True)
    t.start()
    return {"run_id": run_id}

@app.get("/runs/{run_id}/status")
def runs_status(run_id: str):
    return get_status(run_id)

@app.get("/models/champion")
def champion():
    try:
        return load_champion()
    except FileNotFoundError:
        return {"message": "No champion yet."}

@app.post("/predict")
def predict(payload: List[Dict[str, Any]]):
    # Load champion and infer features
    try:
        ch = load_champion()
    except FileNotFoundError:
        return {"preds": [], "message": "No champion available yet."}
    from joblib import load
    import numpy as np
    pipe_path = ch["artifacts"]["pipeline"]
    pipe = load(pipe_path)

    # Ensure all required features exist; missing -> 0
    feats = ch["features"]
    rows = []
    for row in payload:
        rows.append([row.get(f, 0.0) for f in feats])
    X = np.array(rows)
    prob = getattr(pipe.named_steps["clf"], "predict_proba", None)
    if prob:
        preds = pipe.predict_proba(X)[:, 1].tolist()
    else:
        raw = pipe.decision_function(X)
        preds = (1 / (1 + np.exp(-raw))).tolist()
    return {"preds": preds}