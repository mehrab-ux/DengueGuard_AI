
import joblib
import pandas as pd
from pathlib import Path

# Project paths
ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "models" / "dengue_model_smote.joblib"

# Load trained model
saved_data = joblib.load(MODEL_PATH)

model = saved_data["model"]
features = saved_data["features"]
thresholds = saved_data["thresholds"]

print("DengueGuard AI Model Loaded Successfully!")

print("\nRequired Input Features:")
for feature in features:
    print("-", feature)


def predict_dengue_risk(input_data):

    # Create input DataFrame
    input_df = pd.DataFrame([input_data])

    # Ensure correct feature order
    input_df = input_df[features]

    # Match ward_id type to the encoder's training categories
    encoder = model.named_steps["preprocessor"].named_transformers_["ward"]
    input_df["ward_id"] = input_df["ward_id"].astype(
        encoder.categories_[0].dtype
    )

    # Make prediction
    prediction = model.predict(input_df)

    return prediction[0]


# Example input
sample_input = {
    "ward_id": 1,
    "cases_lag_1": 10,
    "avg_temp_c_lag_1": 28.5,
    "avg_temp_c_lag_2": 29.0,
    "avg_temp_c_lag_3": 28.0,
    "avg_temp_c_lag_4": 27.5,
    "rainfall_mm_lag_1": 45.0,
    "rainfall_mm_lag_2": 50.0,
    "rainfall_mm_lag_3": 35.0,
    "rainfall_mm_lag_4": 40.0,
    "relative_humidity_pct_lag_1": 80.0,
    "relative_humidity_pct_lag_2": 82.0,
    "relative_humidity_pct_lag_3": 78.0,
    "relative_humidity_pct_lag_4": 85.0
}

result = predict_dengue_risk(sample_input)

print("\nPredicted Dengue Risk:", result)
