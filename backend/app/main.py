from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import os
import shutil
import logging
import pandas as pd # Make sure pandas is installed

# The start_run function from your core orchestrator logic
from .core.orchestrator import start_run

# --- Application Setup and Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the FastAPI app
app = FastAPI()

# Directory to save uploaded datasets. This directory MUST be writable.
DATA_DIR = "data"
# Create the data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# --- Pydantic Model for Request Body Validation ---
class RunRequest(BaseModel):
    """
    Defines the expected structure for the run start request.
    This helps FastAPI validate incoming JSON payloads.
    """
    dataset_id: str
    target: str
    n_trials: int

# --- API Endpoints ---

@app.get("/")
def read_root():
    """
    A simple root endpoint to check if the server is running.
    This will now successfully return a 200 OK message.
    """
    logger.info("GET request to root endpoint received.")
    return {"message": "Welcome to the Neurogenx AI API! The server is running."}


@app.post("/datasets/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """
    Handles the dynamic uploading of a CSV file.
    The file is saved directly to the server's 'data' directory.
    This endpoint replaces the need to manually add files to Git.
    """
    try:
        # Construct the full path where the file will be saved
        file_path = os.path.join(DATA_DIR, file.filename)
        
        # Use a more robust way to handle file I/O
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Successfully uploaded dataset: {file.filename}")
        return {"filename": file.filename, "message": "File uploaded successfully."}
    except Exception as e:
        logger.error(f"Error during file upload: {e}")
        # Return a 500 error if something goes wrong
        raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")


@app.post("/runs/start")
def runs_start(req: RunRequest):
    """
    Starts a new machine learning run using the specified dataset.
    This will now find the file you previously uploaded via the /datasets/upload endpoint.
    """
    try:
        logger.info(f"Starting run with request: {req.dict()}")
        # Call the orchestrator function with the request payload
        run_id = start_run(req.dict())
        return {"run_id": run_id}
    except Exception as e:
        logger.error(f"Error starting run: {e}")
        # Return a 500 error if something goes wrong during the run
        raise HTTPException(status_code=500, detail=str(e))

