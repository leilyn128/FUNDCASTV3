# backend/retrain_prophet.py
import os
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
from prophet import Prophet
from supabase import create_client

# -----------------------------
# SUPABASE CONFIG
# -----------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None
# -----------------------------
# PATHS
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
FORECAST_PATH = MODELS_DIR / "locked_forecast.csv"
META_PATH = MODELS_DIR / "meta.json"

MODELS_DIR.mkdir(exist_ok=True)

# -----------------------------
# LOAD DATA FROM SUPABASE
# -----------------------------
def load_yearly_data():
    global supabase

    if supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError("Supabase credentials not set")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    response = (
        supabase
        .from_("yearly_budget")
        .select("year,total_income")
        .order("year")
        .execute()
    )

    if not response.data:
        raise ValueError("No data found in Supabase")

    df = pd.DataFrame(response.data)
    df["year"] = df["year"].astype(int)
    df["total_income"] = df["total_income"].astype(float)

    return df

# -----------------------------
# YEAR-CHECK RETRAIN LOGIC
# -----------------------------
def retrain_if_needed():
    current_year = datetime.now().year

    # Load metadata
    if META_PATH.exists():
        meta = json.loads(META_PATH.read_text())
        last_trained_year = meta.get("last_trained_year", 0)
    else:
        last_trained_year = 0

    # Already trained this year → exit
    if current_year <= last_trained_year:
        print("ℹ️ Model already trained for year", last_trained_year)
        return

    print("🔄 New year detected — retraining Prophet model")

    # Load and prepare data
    df = load_yearly_data()
    df = df.rename(columns={"year": "ds", "total_income": "y"})
    df["ds"] = pd.to_datetime(df["ds"], format="%Y")

    # Train model
    model = Prophet()
    model.fit(df)

    # Forecast next 5 years
    future = model.make_future_dataframe(periods=3, freq="Y")
    forecast = model.predict(future)

    result = forecast[["ds", "yhat"]].tail(5)
    result["year"] = result["ds"].dt.year
    result.rename(columns={"yhat": "prediction"}, inplace=True)
    result = result[["year", "prediction"]]

    # Save locked forecast
    result.to_csv(FORECAST_PATH, index=False)

    # Update metadata
    META_PATH.write_text(
        json.dumps({"last_trained_year": current_year}, indent=2)
    )

    print("✅ Retraining completed for year", current_year)

# -----------------------------
# MANUAL RUN (OPTIONAL)
# -----------------------------
if __name__ == "__main__":
    retrain_if_needed()