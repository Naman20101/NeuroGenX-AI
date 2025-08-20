import json, os, glob
from typing import Any, Dict
from joblib import load, dump
from datetime import datetime

MODELS_DIR = "models"

def _latest_manifest():
    manifests = glob.glob(os.path.join(MODELS_DIR, "run_*", "model.manifest.json"))
    if not manifests:
        return None
    manifests.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return manifests[0]

def save_champion(run_id: str, pipeline, model, metrics: Dict[str, float]):
    run_dir = os.path.join(MODELS_DIR, f"run_{run_id}")
    os.makedirs(run_dir, exist_ok=True)
    dump(pipeline, os.path.join(run_dir, "pipeline.pkl"))
    dump(model,    os.path.join(run_dir, "model.pkl"))
    manifest = {
        "run_id": run_id,
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": metrics,
        "artifacts": {
            "pipeline": "pipeline.pkl",
            "model": "model.pkl"
        }
    }
    with open(os.path.join(run_dir, "model.manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    return manifest

def load_latest():
    mpath = _latest_manifest()
    if not mpath:
        return None
    run_dir = os.path.dirname(mpath)
    with open(mpath) as f:
        manifest = json.load(f)
    pipeline = load(os.path.join(run_dir, "pipeline.pkl"))
    model    = load(os.path.join(run_dir, "model.pkl"))
    return {"manifest": manifest, "pipeline": pipeline, "model": model}