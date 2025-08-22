from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil, os

router = APIRouter()

UPLOAD_DIR = "/tmp"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Validate file type (CSV expected)
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Only CSV files allowed")

        # Quick peek into dataset
        import pandas as pd
        df = pd.read_csv(file_path)
        columns = list(df.columns)
        dtypes = {col: str(df[col].dtype) for col in columns}

        return {"dataset_id": file.filename, "columns": columns, "dtypes": dtypes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
