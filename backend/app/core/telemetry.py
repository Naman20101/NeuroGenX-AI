from typing import Dict
from datetime import datetime

# Minimal in-memory telemetry for MVP. Replace with OTEL/Prometheus later.
# Matches "observability-first" principle from your plan. 
_RUNS: Dict[str, dict] = {}

def init_run(run_id: str, payload: dict):
    _RUNS[run_id] = {"status": "starting", "payload": payload, "events": []}

def log(run_id: str, stage: str, data: dict):
    if run_id not in _RUNS: return
    _RUNS[run_id]["events"].append({"t": datetime.utcnow().isoformat(), "stage": stage, "data": data})
    _RUNS[run_id]["status"] = stage

def get(run_id: str):
    return _RUNS.get(run_id, {"status": "unknown"})