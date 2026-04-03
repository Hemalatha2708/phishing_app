import pandas as pd
from features import extract_features

# Load dataset
df = pd.read_csv("phishing_urls.csv")

# Keep only required columns
df = df[['url', 'label']]

# Remove missing values
df = df.dropna()

# Remove duplicates
df = df.drop_duplicates()

print("Total cleaned samples:", len(df))

# Convert URLs → features
X = df['url'].apply(lambda x: extract_features(x)).tolist()
y = df['label']

print("Sample features:", X[0])
print(df.columns)