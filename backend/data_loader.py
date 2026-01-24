from database import get_budget_data
import pandas as pd

def load_yearly_income():
    query = """
        SELECT
            EXTRACT(YEAR FROM date) AS year,
            SUM(amount) AS amount
        FROM transactions
        WHERE type = 'income'
        GROUP BY year
        ORDER BY year
    """

    df = get_budget_data()
    
    return df
