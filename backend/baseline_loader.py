import pandas as pd

BASELINE_PATH = "data/budgets.csv"

def load_baseline_data():
    df = pd.read_csv(BASELINE_PATH)

    # Match Colab exactly
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

    df["year"] = df["year"].astype(int)
    df = df.sort_values("year")

    yearly = (
        df
        .groupby("year")
        .agg({
            "amount": "sum",
            "population": "mean"
        })
        .reset_index()
    )

    # Prophet-ready
    yearly["ds"] = pd.to_datetime(yearly["year"].astype(str) + "-01-01")
    yearly["y"] = yearly["amount"]

    return yearly[["ds", "y"]]
