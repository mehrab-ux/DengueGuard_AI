import pandas as pd
from features import create_features

df = pd.read_csv("../cleaned_dengue_data.csv")

df = create_features(df)

print("Feature engineering completed!")
print("\nNew columns:")
print(df.columns.tolist())

print("\nFirst 10 rows of new features:")
print(df[[
    "ward_id",
    "date",
    "rainfall_lag_1",
    "rainfall_lag_2",
    "rainfall_lag_3",
    "rainfall_lag_4",
    "rainfall_4week_total",
    "humidity_4week_avg",
    "cases_lag_1"
]].head(10))

print("\nDataset shape after feature engineering:")
print(df.shape)