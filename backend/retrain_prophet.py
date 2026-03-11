from prophet import Prophet
import pandas as pd
import joblib
import os
import json
from datetime import datetime
from data_loader import load_all_yearly_income

MODEL_PATH = "models/prophet2.pkl"
META_PATH = "models/meta.json"

def retrain_if_needed(force=False):
    print("🚀 retrain_if_needed called | force =", force)

    df = load_all_yearly_income()
    print("📊 Loaded data shape:", df.shape)

    current_year = datetime.now().year
    last_retrain_year = None

    if os.path.exists(META_PATH):
        with open(META_PATH, "r") as f:
            last_retrain_year = json.load(f).get("last_retrain_year")

    print("📅 Last retrain year:", last_retrain_year)

    if not force and last_retrain_year == current_year and os.path.exists(MODEL_PATH):
        print("✅ Model already trained for this year")
        return

    print("🔥 Training Prophet model now...")

    model = Prophet(
        yearly_seasonality=False,
        weekly_seasonality=False,
        daily_seasonality=False,
        changepoint_prior_scale=0.5,
        seasonality_prior_scale=10.0
    )

    model.fit(df)
    print("✅ Model fit complete")

    joblib.dump(model, MODEL_PATH)
    print("💾 Model saved to", MODEL_PATH)

    with open(META_PATH, "w") as f:
        json.dump({"last_retrain_year": current_year}, f)

def get_forecast(years_ahead=3):
    print("📡 get_forecast called | years_ahead =", years_ahead)

    try:
        model = joblib.load(MODEL_PATH)
        print("📦 Model loaded successfully")
    except Exception as e:
        print("❌ Model load failed:", e)
        print("🔁 Forcing retrain...")
        retrain_if_needed(force=True)
        model = joblib.load(MODEL_PATH)

    last_date = model.history["ds"].max()

    future = pd.DataFrame({
        "ds": pd.date_range(
            start=last_date + pd.DateOffset(years=1),
            periods=years_ahead,
            freq="YS"
        )
    })
    forecast = model.predict(future)

    last_train_date = model.history["ds"].max()
    future_only = forecast[forecast["ds"] > last_train_date]

    print("📈 Forecast rows:", len(future_only))

    return future_only[["ds", "yhat"]]
