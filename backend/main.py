# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from pathlib import Path
import pandas as pd
from scheduler import scheduler

# -----------------------------
# PATH FIX (THIS IS THE KEY)
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
LOCKED_FORECAST_PATH = BASE_DIR / "models" / "locked_forecast.csv"

app = FastAPI()

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://fundcast-api.onrender.com",  # optional
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# ROOT
# -----------------------------
@app.get("/")
def root():
    return {"message": "Prophet API (LOCKED forecast, read-only)"}

# -----------------------------
# FORECAST ENDPOINT (LOCKED)
# -----------------------------
@app.get("/forecast")
def forecast():
    try:
        if not LOCKED_FORECAST_PATH.exists():
            raise FileNotFoundError(
                f"Forecast file not found at {LOCKED_FORECAST_PATH}"
            )

        df = pd.read_csv(LOCKED_FORECAST_PATH)
        return df.to_dict(orient="records")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))