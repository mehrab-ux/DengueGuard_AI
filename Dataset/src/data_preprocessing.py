
import pandas as pd
from pathlib import Path

# Find the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load the original dataset
data_path = PROJECT_ROOT / "Dataset" / "dengue_data.csv"
df = pd.read_csv(data_path)

# Remove duplicate records
df = df.drop_duplicates()

# Convert date column into datetime format
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Remove rows with invalid dates
df = df.dropna(subset=["date"])

# Sort data by ward and date
df = df.sort_values(["ward_id", "date"])

# Save cleaned dataset
output_path = PROJECT_ROOT / "Dataset" / "cleaned_dengue_data.csv"
df.to_csv(output_path, index=False)

print("Data preprocessing completed!")
print("Dataset shape:", df.shape)
print("\nMissing values:")
print(df.isnull().sum())
print("\nDate range:", df["date"].min(), "to", df["date"].max())
