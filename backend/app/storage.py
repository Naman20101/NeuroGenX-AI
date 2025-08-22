import os, json, time, uuid, shutil
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import io

# Prefer Render-safe temp. Fallback to repo-local.
ROOT = Path(os.getenv("NG1_RUNTIME_DIR", "/tmp/ng1"))
if not ROOT.exists():
    try:
        ROOT.mkdir(parents=True, exist_ok=True)
    except Exception:
        ROOT = Path("./runtime")
        ROOT.mkdir(parents=True, exist_ok=True)

DATA_DIR = ROOT / "data"
MODELS_DIR = ROOT / "models"
RUNS_DIR = ROOT / "runs"
for d in (DATA_DIR, MODELS_DIR, RUNS_DIR):
    d.mkdir(parents=True, exist_ok=True)

def save_dataset(contents: bytes, dataset_id: str) -> str:
    """Saves file contents to DATA_DIR with dataset_id as the name."""
    dst = DATA_DIR / dataset_id
    with open(dst, "wb") as f:
        f.write(contents)
    return str(dst)

def load_csv(dataset_id: str) -> pd.DataFrame:
    p = DATA_DIR / dataset_id
    if not p.exists():
        raise FileNotFoundError(f"Dataset not found: {p}")
    return pd.read_csv(p, low_memory=False)

def new_run() -> str:
    return uuid.uuid4().hex[:12]

def run_file(run_id: str) -> Path:
    return RUNS_DIR / f"{run_id}.json"

def append_event(run_id: str, stage: str, data: Dict[str, Any]):
    f = run_file(run_id)
    if f.exists():
        js = json.loads(f.read_text())
    else:
        js = {"status": "running", "events": []}
    js["events"].append({"ts": time.time(), "stage": stage, "data": data})
    f.write_text(json.dumps(js))

def set_status(run_id: str, status: str):
    f = run_file(run_id)
    js = json.loads(f.read_text()) if f.exists() else {"events": []}
    js["status"] = status
    f.write_text(json.dumps(js))

def get_status(run_id: str) -> Dict[str, Any]:
    f = run_file(run_id)
    if not f.exists():
        return {"status": "unknown", "events": []}
    return json.loads(f.read_text())

def save_champion(manifest: Dict[str, Any]):
    (MODELS_DIR / "champion.json").write_text(json.dumps(manifest))

def load_champion() -> Dict[str, Any]:
    p = MODELS_DIR / "champion.json"
    if not p.exists():
        raise FileNotFoundError("No champion yet.")
    return json.loads(p.read_text())

def model_dir_for(run_id: str) -> Path:
    p = MODELS_DIR / f"run_{run_id}"
    p.mkdir(parents=True, exist_ok=True)
    return p
