from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import os, joblib, uuid
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

router = APIRouter()

RUNS = {}
CHAMPION_PATH = "/tmp/models/champion.pkl"

os.makedirs("/tmp/models", exist_ok=True)

class RunRequest(BaseModel):
    dataset_id: str
    target: str
    n_trials: int = 5

@router.post("/start")
async def start_run(req: RunRequest):
    try:
        dataset_path = f"/tmp/{req.dataset_id}"
        if not os.path.exists(dataset_path):
            raise HTTPException(status_code=404, detail="Dataset not found")

        df = pd.read_csv(dataset_path)
        if req.target not in df.columns:
            raise HTTPException(status_code=400, detail=f"Target {req.target} not in dataset")

        X = df.drop(columns=[req.target])
        y = df[req.target]

        # Split dataset
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        # Candidate models
        models = {
            "RandomForest": RandomForestClassifier(n_estimators=50, random_state=42),
            "LogisticRegression": LogisticRegression(max_iter=200)
        }

        best_model, best_auc, best_f1 = None, -1, -1
        for name, model in models.items():
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            probs = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else preds
            auc = roc_auc_score(y_test, probs)
            f1 = f1_score(y_test, preds)
            if auc > best_auc:
                best_auc, best_f1, best_model = auc, f1, (name, model)

        # Save champion
        joblib.dump(best_model[1], CHAMPION_PATH)

        run_id = str(uuid.uuid4())
        RUNS[run_id] = {
            "status": "done",
            "model": best_model[0],
            "metrics": {"auc": best_auc, "f1": best_f1}
        }

        return {
            "message": "Run completed",
            "run_id": run_id,
            "champion": {
                "family": best_model[0],
                "metrics": {"auc": best_auc, "f1": best_f1}
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
