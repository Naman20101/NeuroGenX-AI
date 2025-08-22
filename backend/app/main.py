from __future__ import annotations
import os, io, threading, traceback, uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import orjson
import pandas as pd
import logging
import uuid
from .core.schemas import RunRequest
from .storage import save_dataset, load_csv, new_run, append_event, set_status, get_status, load_champion
from .core.training import train_genetic

# Set up logging for better visibility into what's happening
logging.basicConfig(level=logging.INFO)

# Initialize the FastAPI app with a default response class that allows for flexibility.
app = FastAPI(title="NeuroGenX NG-1 v2")

# Add middleware for CORS to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

@app.get("/")
async def root() -> Dict[str, str]:
    """
    Root endpoint to confirm the API is running.
    Returns a JSON message.
    """
    logging.info("Root endpoint accessed successfully.")
    return {"message": "NeuroGenX API v2 running."}

@app.post("/datasets/upload")
async def upload_dataset(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Handles the upload of a CSV dataset, saves it, and returns a summary.
    This version generates a unique ID and saves the file directly.
    """
    try:
        logging.info(f"Received upload request for file: {file.filename}")
        
        # Generate a unique ID for the dataset
        dataset_id = str(uuid.uuid4())

        # Read the file contents directly from the upload stream
        contents = await file.read()
        
        # Save the dataset directly using the new unique ID
        dst = save_dataset(contents, dataset_id)
        
        # Read a quick peek of the CSV to get columns and dtypes
        df = pd.read_csv(io.BytesIO(contents), nrows=100)
        cols = list(df.columns)
        dtypes = {c: str(df[c].dtype) for c in cols}
        
        logging.info(f"Dataset {dataset_id} processed. Columns: {cols}")
        return {"dataset_id": dataset_id, "columns": cols, "dtypes": dtypes}
    except Exception as e:
        logging.error(f"Error during dataset upload: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process the dataset: {str(e)}")


def _background_train(run_id: str, req: RunRequest):
    """
    This function runs in the background to start the training process.
    """
    try:
        logging.info(f"Background training started for run_id: {run_id}")
        df = load_csv(req.dataset_id)
        res = train_genetic(run_id, df, req.target, req.n_trials)
        if not res.get("ok"):
            set_status(run_id, "error")
            append_event(run_id, "error", {"msg": res.get("error", "unknown")})
            logging.error(f"Training failed for run {run_id}: {res.get('error', 'unknown')}")
        else:
            logging.info(f"Training for run {run_id} completed successfully.")
    except Exception as e:
        logging.error(f"An unexpected error occurred during background training for run {run_id}", exc_info=True)
        set_status(run_id, "error")
        append_event(run_id, "error", {
            "msg": str(e),
            "trace": traceback.format_exc()[:5000]
        })

@app.post("/runs/start")
async def runs_start(req: RunRequest):
    """
    Launches a new model training run in a background thread.
    """
    run_id = new_run()
    append_event(run_id, "start", req.dict())
    set_status(run_id, "running")
    t = threading.Thread(target=_background_train, args=(run_id, req), daemon=True)
    t.start()
    logging.info(f"Model run started with run_id: {run_id}")
    return {"run_id": run_id}

@app.get("/runs/{run_id}/status")
async def runs_status(run_id: str):
    """
    Gets the live status of a model run.
    """
    status = get_status(run_id)
    logging.info(f"Status requested for run {run_id}. Status: {status}")
    return status

@app.get("/models/champion")
async def champion():
    """
    Returns the champion model if one exists.
    """
    try:
        champion_data = load_champion()
        logging.info("Champion model loaded successfully.")
        return champion_data
    except FileNotFoundError:
        logging.info("No champion model found.")
        raise HTTPException(status_code=404, detail="No champion model has been found yet.")

@app.post("/predict")
async def predict(payload: List[Dict[str, Any]]):
    """
    Makes a prediction using the champion model.
    """
    try:
        champion_data = load_champion()
    except FileNotFoundError:
        logging.warning("Prediction requested but no champion model available.")
        return {"preds": [], "message": "No champion available yet."}
    
    # Rest of the prediction logic (joblib, numpy)
    from joblib import load
    import numpy as np
    pipe_path = champion_data["artifacts"]["pipeline"]
    pipe = load(pipe_path)
    feats = champion_data["features"]
    
    rows = [[row.get(f, 0.0) for f in feats] for row in payload]
    X = np.array(rows)
    
    prob = getattr(pipe.named_steps["clf"], "predict_proba", None)
    if prob:
        preds = pipe.predict_proba(X)[:, 1].tolist()
    else:
        raw = pipe.decision_function(X)
        preds = (1 / (1 + np.exp(-raw))).tolist()
        
    logging.info(f"Prediction made for {len(payload)} items.")
    return {"preds": preds}

