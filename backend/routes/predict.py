from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import joblib, os
import pandas as pd

router = APIRouter()

CHAMPION_PATH = "/tmp/models/champion.pkl"

class PredictRequest(BaseModel):
    rows: list

@router.post("/")
async def predict(req: PredictRequest):
    if not os.path.exists(CHAMPION_PATH):
        raise HTTPException(status_code=404, detail="Champion model not found")

    model = joblib.load(CHAMPION_PATH)

    # Convert rows to DataFrame
    try:
        df = pd.DataFrame(req.rows)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")

    preds = model.predict(df).tolist()
    return {"predictions": preds}
