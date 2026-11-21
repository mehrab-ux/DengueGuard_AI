
import pandas as pd
import numpy as np
import joblib
from pathlib import Path

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.utils.class_weight import compute_class_weight
from imblearn.ensemble import BalancedRandomForestClassifier
from imblearn.over_sampling import SMOTENC
# Project paths
ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = r"Dataset/cleaned_dengue_data.csv"
MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(exist_ok=True)

# Load dataset
df = pd.read_csv(DATA_PATH)
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["ward_id", "date"]).copy()

# Create next-week dengue cases as the prediction target
df["next_week_cases"] = (
    df.groupby("ward_id")["dengue_cases"].shift(-1)
)

# Create previous-week weather and dengue features
weather_columns = [
    "avg_temp_c",
    "rainfall_mm",
    "relative_humidity_pct"
]

for column in weather_columns:
    for week in range(1, 5):
        df[f"{column}_lag_{week}"] = (
            df.groupby("ward_id")[column].shift(week)
        )

# Previous week's dengue cases
df["cases_lag_1"] = (
    df.groupby("ward_id")["dengue_cases"].shift(1)
)

# Remove rows without enough historical data
df = df.dropna().copy()

# Chronological train/test split
split_date = df["date"].quantile(0.8)

train = df[df["date"] <= split_date].copy()
test = df[df["date"] > split_date].copy()

if train.empty or test.empty:
    raise ValueError("Not enough data for chronological train/test split.")

# Define risk levels using training data only
thresholds = train["next_week_cases"].quantile(
    [0.50, 0.80, 0.95]
).to_list()

def assign_risk(cases):
    if cases <= thresholds[0]:
        return "Low"
    elif cases <= thresholds[1]:
        return "Medium"
    elif cases <= thresholds[2]:
        return "High"
    return "Critical"

train["risk_level"] = train["next_week_cases"].apply(assign_risk)
test["risk_level"] = test["next_week_cases"].apply(assign_risk)

# Select features
lag_features = [
    f"{column}_lag_{week}"
    for column in weather_columns
    for week in range(1, 5)
]

features = ["ward_id", "cases_lag_1"] + lag_features

X_train = train[features]
y_train = train["risk_level"]

X_test = test[features]
y_test = test["risk_level"]


# Apply SMOTENC only to training data
smote = SMOTENC(
    categorical_features=[0],
    sampling_strategy="not majority",
    random_state=42,
    k_neighbors=5
)

X_train_smote, y_train_smote = smote.fit_resample(
    X_train,
    y_train
)

print("\nClass distribution after SMOTENC:")
print(y_train_smote.value_counts())

print("\nOriginal training class distribution:")
print(y_train.value_counts())

# Preprocess ward ID and train the model
preprocessor = ColumnTransformer(
    transformers=[
        ("ward", OneHotEncoder(handle_unknown="ignore"), ["ward_id"])
    ],
    remainder="passthrough"
)

# Build Balanced Random Forest model
model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", BalancedRandomForestClassifier(
        n_estimators=300,
        random_state=42,
        sampling_strategy="all",
        replacement=True,
        n_jobs=-1
    ))
])


# Train model
model.fit(X_train_smote, y_train_smote)


# Evaluate
predictions = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, predictions))
print("\nClassification Report:")
print(classification_report(
    y_test,
    predictions,
    labels=["Low", "Medium", "High", "Critical"],
    zero_division=0
))

# Save model and prediction information
joblib.dump({
    "model": model,
    "features": features,
    "thresholds": thresholds
}, MODEL_DIR / "dengue_model_smote.joblib")

print("\nModel saved successfully!")
print("Location:", MODEL_DIR / "dengue_model_smote.joblib")
print("Train rows:", len(train))
print("Test rows:", len(test))
print("Chronological split date:", split_date)
