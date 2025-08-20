import os, pandas as pd

def load_csv(dataset_id: str) -> pd.DataFrame:
    path = os.path.join("data", dataset_id)
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found")
    return pd.read_csv(path)