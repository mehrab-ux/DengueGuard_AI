import pandas as pd

def create_features(df):

    df = df.copy()

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["ward_id", "date"])

    df["rainfall_lag_1"] = df.groupby("ward_id")["rainfall_mm"].shift(1)
    df["rainfall_lag_2"] = df.groupby("ward_id")["rainfall_mm"].shift(2)
    df["rainfall_lag_3"] = df.groupby("ward_id")["rainfall_mm"].shift(3)
    df["rainfall_lag_4"] = df.groupby("ward_id")["rainfall_mm"].shift(4)

    df["rainfall_4week_total"] = (
        df.groupby("ward_id")["rainfall_mm"]
        .rolling(4)
        .sum()
        .reset_index(level=0, drop=True)
    )

    df["humidity_4week_avg"] = (
        df.groupby("ward_id")["relative_humidity_pct"]
        .rolling(4)
        .mean()
        .reset_index(level=0, drop=True)
    )

    df["cases_lag_1"] = df.groupby("ward_id")["dengue_cases"].shift(1)

    return df