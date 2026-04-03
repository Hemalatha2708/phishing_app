import pandas as pd

# Load datasets
phishing = pd.read_csv("phishing_urls.csv")
legit = pd.read_csv("legit.csv")

# ✅ IMPORTANT FIX: keep only phishing
phishing = phishing[phishing['label'] == 1]

print("Before balancing:")
print("Phishing:", len(phishing))
print("Legit:", len(legit))

# Balance
legit = legit.sample(n=len(phishing), random_state=42)

print("After balancing:")
print("Legit:", len(legit))

# Combine
df = pd.concat([phishing, legit])

# Shuffle
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Save
df.to_csv("final_data.csv", index=False)

print("✅ Final dataset size:", len(df))
print("Final labels:\n", df['label'].value_counts())

# Debug (optional)
print("Original phishing file labels:\n", pd.read_csv("phishing_urls.csv")['label'].value_counts())

