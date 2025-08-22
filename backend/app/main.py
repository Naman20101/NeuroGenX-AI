from fastapi import FastAPI
from routes import runs, models, predict

app = FastAPI(title="NeuroGenX NG-1 v2")

@app.get("/")
async def root():
    return {"message": "NeuroGenX v2 API is running"}

# Include routers
app.include_router(runs.router, prefix="/runs", tags=["Runs"])
app.include_router(models.router, prefix="/models", tags=["Models"])
app.include_router(predict.router, prefix="/predict", tags=["Predict"])


