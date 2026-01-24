# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from retrain_prophet import retrain_if_needed
import pandas as pd


# PATH FIX
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
        "http://192.168.100.180:3000",   # local network
        "https://fundcast-api.onrender.com",
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
# FORECAST ENDPOINT
# -----------------------------
@app.get("/forecast")
def forecast():
    try:
        # 🔄 Free annual auto-retrain (year-check logic)
        retrain_if_needed()

        # 🔒 Locked forecast must exist
        if not LOCKED_FORECAST_PATH.exists():
            raise HTTPException(
                status_code=500,
                detail="Locked forecast file not found. Model may not be trained yet."
            )

        df = pd.read_csv(LOCKED_FORECAST_PATH)
        return df.to_dict(orient="records")

    except HTTPException:
        raise  # rethrow intended API errors

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Forecast generation failed: {str(e)}"
        )