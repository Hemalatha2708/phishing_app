import pandas as pd

# Load Tranco dataset
df = pd.read_csv("legit.csv", header=None)

# Rename columns
df.columns = ['rank', 'domain']

# Convert domain → URL
df['url'] = "https://" + df['domain']

# Add label (0 = legit)
df['label'] = 0

# Keep only required columns
df = df[['url', 'label']]

# ✅ Take EXACT same count as phishing dataset
df = df.head(48812)

# Save
df.to_csv("legit.csv", index=False)

print("✅ Legit dataset created:", len(df))