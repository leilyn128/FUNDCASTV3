import pandas as pd
from baseline_loader import load_baseline_data
from database import get_budget_data

def load_all_yearly_income():
    # Baseline (Colab)
    baseline = load_baseline_data()
    baseline["year"] = baseline["ds"].dt.year

    # Newly inputted (Supabase)
    new_data = get_budget_data()  # year | total_income
    new_data["year"] = new_data["year"].astype(int)
    new_data["y"] = new_data["total_income"]

    # Combine
    df = pd.concat([
        baseline[["year", "y"]],
        new_data[["year", "y"]]
    ])

    # Remove duplicates (new data overrides baseline)
    df = df.sort_values("year").drop_duplicates("year", keep="last")

    # Prophet format
    df["ds"] = pd.to_datetime(df["year"].astype(str) + "-01-01")

    return df[["ds", "y"]]
