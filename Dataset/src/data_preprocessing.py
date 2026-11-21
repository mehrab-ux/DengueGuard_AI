import pandas as pd

df = pd.read_csv("dataset/dengue_data.csv")

# Remove duplicate rows
df = df.drop_duplicates()

# Convert date column
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Remove invalid dates
df = df.dropna(subset=["date"])

# Check missing values
print("\nMissing Values:")
print(df.isnull().sum())


# Save cleaned dataset
df.to_csv("dataset/cleaned_dengue_data.csv", index=False)

print("\nCleaned dataset saved successfully!")

# Verify date conversion
print("\nDate column type:")
print(df["date"].dtype)

# Check dataset dimensions
print("\nDataset Shape:")
print(df.shape)