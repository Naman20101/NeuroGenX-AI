from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List
from pathlib import Path
import shutil
import pandas as pd
import logging

from app.core.orchestrator import start_run, get_status, load_champion, predict_rows

# --- Configuration and Setup ---

# Define the root directory for uploads using a more robust Path object
UPLOAD_DIR = Path("data")

# Create a logger for better error reporting
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure the upload directory exists on startup
try:
    UPLOAD_DIR.mkdir(exist_ok=True)
except Exception as e:
    logger.error(f"Failed to create upload directory: {e}")
    # You might want to exit the application here if the directory is critical

app = FastAPI(
    title="NeuroGenX AI API",
    description="A robust API for automated machine learning workflows.",
    version="1.0.0",
)

# --- Pydantic Models for Request Validation ---

class StartRunPayload(BaseModel):
    """
    Validates the payload for starting a new run.
    Ensures required fields are present and correctly typed.
    """
    dataset_id: str
    target: str
    n_trials: int

class PredictPayload(BaseModel):
    """
    Validates the payload for making predictions.
    Ensures the 'rows' field is a list of dictionaries.
    """
    rows: List[Dict]

# --- Dependency Injection for Reusable Logic ---

def get_upload_dir() -> Path:
    """Provides the upload directory path."""
    return UPLOAD_DIR

# --- Endpoints with Advanced Error Handling ---

@app.get("/health")
def health():
    """Simple health check endpoint."""
    return {"status": "ok"}

@app.post("/datasets/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    upload_dir: Path = Depends(get_upload_dir)
):
    """
    Uploads a CSV file to the server.
    Handles file saving and returns metadata.
    """
    # Use Path objects for safe and clean file path manipulation
    file_path = upload_dir / file.filename
    
    # Robustly handle the file saving process
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Successfully uploaded and saved file: {file.filename}")
    except Exception as e:
        logger.error(f"Error saving file '{file.filename}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # Robustly handle the file reading for metadata extraction
    try:
        df = pd.read_csv(file_path)
        return {
            "dataset_id": file.filename,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict()
        }
    except Exception as e:
        # If metadata extraction fails, return a 400 Bad Request
        logger.error(f"Error reading file '{file.filename}' for metadata: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid CSV file format: {e}")

@app.post("/runs/start")
def start_run_endpoint(payload: StartRunPayload):
    """
    Starts an automated machine learning run.
    Returns the unique run_id.
    """
    # The orchestrator handles the core logic, so we wrap its call in a try/except
    # to catch any unexpected errors and return a 500 error gracefully.
    try:
        run_id = start_run(payload.dict())
        return {"run_id": run_id}
    except Exception as e:
        logger.error(f"An error occurred while starting run for payload: {payload.dict()}. Error: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred while starting the run.")

@app.get("/runs/{run_id}/status")
def get_run_status(run_id: str):
    """Gets the status and logs for a specific run."""
    status = get_status(run_id)
    if "error" in status:
        raise HTTPException(status_code=404, detail=status["error"])
    return status

@app.get("/champion")
def get_champion():
    """Retrieves metadata for the latest champion model."""
    manifest = load_champion()
    if "detail" in manifest:
        raise HTTPException(status_code=404, detail=manifest["detail"])
    return manifest

@app.post("/predict")
def predict_endpoint(payload: PredictPayload):
    """Makes predictions using the latest deployed champion model."""
    try:
        preds = predict_rows(payload.rows)
        if "detail" in preds:
            raise HTTPException(status_code=404, detail=preds["detail"])
        return preds
    except Exception as e:
        logger.error(f"Prediction failed for payload: {payload.rows}. Error: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed. Check server logs for details.")

