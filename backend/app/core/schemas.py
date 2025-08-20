from pydantic import BaseModel

class RunRequest(BaseModel):
    dataset_id: str
    target: str
    n_trials: int = 40