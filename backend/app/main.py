from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.core.orchestrator import start_run, get_status, load_champion, predict_rows
from app.core.schemas import RunRequest
import pandas as pd
import os

app = FastAPI(title="NeuroGenX NG-1 API") # This is the only app declaration

# This middleware is now part of the correct app instance
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# This route is now correctly associated with the single app instance
@app.get("/")
async def root():
    return {"message": "Welcome to the NeuroGenX AI backend!"}

os.makedirs("data", exist_ok=True)
os.makedirs("models", exist_ok=True)

@app.post("/datasets/upload")
async def upload_dataset(file: UploadFile = File(...)):
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
    run_id = start_run(req.dict())
    # v0.1: run synchronously in a BG task to keep deploy simple
    tasks.add_task(lambda: None)
    return {"run_id": run_id}

@app.get("/runs/{run_id}/status")
def runs_status(run_id: str):
    return get_status(run_id)

@app.get("/models/champion")
def champion():
    return load_champion()

@app.post("/predict")
def predict(rows: list[dict]):
    return {"preds": predict_rows(rows)}
