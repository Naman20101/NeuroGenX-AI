from pydantic import BaseModel, Field, RootModel
from typing import List, Dict, Any, Optional

# This class is correct. No changes needed.
class RunRequest(BaseModel):
    dataset_id: str
    target: str
    n_trials: int = Field(default=12, ge=1, le=200)

# This class is correct. No changes needed.
class RunStatus(BaseModel):
    status: str
    events: List[Dict[str, Any]]

# --- THIS IS THE CORRECTED PART ---
# The '__root__' syntax is now replaced with 'pydantic.RootModel'.
# This is required for Pydantic V2.
class PredictRequest(RootModel):
    """
    Model for prediction requests, representing a list of data points.
    Inherits from RootModel and uses a 'root' attribute for the data.
    """
    root: List[Dict[str, Any]]

# This class is correct. No changes needed.
class ChampionResponse(BaseModel):
    run_id: str
    timestamp: str
    metrics: Dict[str, float]
    model: Dict[str, Any]
    features: List[str]