from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.core.orchestrator import start_run, get_status, load_champion, predict_rows
from app.core.schemas import RunRequest
import pandas as pd
import os

# Set a title and description for the API, which helps the documentation generator.
app = FastAPI(
    title="NeuroGenX NG-1 API",
    description="API for NeuroGenX NG-1, managing datasets, machine learning runs, and predictions."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("data", exist_ok=True)
os.makedirs("models", exist_ok=True)

# Add a root endpoint for a basic health check.
@app.get("/")
def read_root():
    """
    A simple endpoint to confirm the API is up and running.
    """
    return {"message": "Welcome to the NeuroGenX NG-1 API! The server is running."}

@app.post("/datasets/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """
    Uploads a dataset CSV file to the 'data' directory.
    """
    path = os.path.join("data", file.filename)
    with open(path, "wb") as f:
        f.write(await file.read())
    # simple schema infer
    df = pd.read_csv(path, nrows=200)
    cols = df.columns.tolist()
    dtypes = {c: str(df[c].dtype) for c in cols}
    return {"dataset_id": file.filename, "columns": cols, "dtypes": dtypes}

@app.post("/runs/start")
def runs_start(req: RunRequest, tasks: BackgroundTasks):
    """
    Starts a new machine learning run in the background.
    """
    run_id = start_run(req.dict())
    # v0.1: run synchronously in a BG task to keep deploy simple
    tasks.add_task(lambda: None)
    return {"run_id": run_id}

@app.get("/runs/{run_id}/status")
def runs_status(run_id: str):
    """
    Retrieves the status of a specific run.
    """
    return get_status(run_id)

@app.get("/models/champion")
def champion():
    """
    Loads and returns information about the current champion model.
    """
    return load_champion()

@app.post("/predict")
def predict_model(data: PredictionInput):
    print("Received data:", data)  # See what data the API is getting.
    prediction = some_prediction_function(data)
    print("Model output:", prediction)  # See what the model is returning.
    return {"prediction": prediction}

