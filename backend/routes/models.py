from fastapi import APIRouter, HTTPException
import os

router = APIRouter()

CHAMPION_PATH = "/tmp/models/champion.pkl"

@router.get("/champion")
async def get_champion():
    if not os.path.exists(CHAMPION_PATH):
        raise HTTPException(status_code=404, detail="Champion not found")
    return {"message": "Champion is available"}
