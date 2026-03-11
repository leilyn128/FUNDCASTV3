from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from retrain_prophet import retrain_if_needed, get_forecast

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.100.180:3000",
        "https://fundcast-ui.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Prophet API (model-based forecast)"}

@app.get("/forecast")
def forecast(years_ahead: int = 3):
    retrain_if_needed()
    df = get_forecast(years_ahead=years_ahead)
    return df.to_dict(orient="records")
