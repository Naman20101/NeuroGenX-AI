from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import pandas as pd
import os
import shutil
import logging
from .core.orchestrator import start_run

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Directory to save uploaded datasets
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

class RunRequest(BaseModel):
    dataset_id: str
    target: str
    n_trials: int

@app.post("/datasets/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """
    Endpoint to upload a new dataset.
    The file will be saved to the 'data/' directory on the server.
    """
    try:
        file_path = os.path.join(DATA_DIR, file.filename)
        # Use shutil.copyfileobj for efficient file writing
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Successfully uploaded dataset: {file.filename}")
        return {"filename": file.filename, "message": "File uploaded successfully."}
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")


@app.post("/runs/start")
def runs_start(req: RunRequest):
    """
    Endpoint to start a new run with the uploaded dataset.
    """
    try:
        logger.info(f"Starting run with request: {req.dict()}")
        run_id = start_run(req.dict())
        return {"run_id": run_id}
    except Exception as e:
        logger.error(f"Error starting run: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to the Neurogenx AI API!"}

