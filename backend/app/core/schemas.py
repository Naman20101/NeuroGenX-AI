from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class RunRequest(BaseModel):
    dataset_id: str
    target: str
    n_trials: int = Field(default=12, ge=1, le=200)

class RunStatus(BaseModel):
    status: str
    events: List[Dict[str, Any]]

class PredictRequest(BaseModel):
    __root__: List[Dict[str, Any]]

class ChampionResponse(BaseModel):
    run_id: str
    timestamp: str
    metrics: Dict[str, float]
    model: Dict[str, Any]
    features: List[str]