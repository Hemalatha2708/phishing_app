import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
import joblib

from features import extract_features

# Load dataset
df = pd.read_csv("final_data_new.csv")

# Extract features
X = [extract_features(url) for url in df['url']]
y = df['label']

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -------------------
# Random Forest
rf = RandomForestClassifier(n_estimators=100)
rf.fit(X_train, y_train)

rf_pred = rf.predict(X_test)
print("RF Accuracy:", accuracy_score(y_test, rf_pred))

# -------------------
# XGBoost
xgb = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
xgb.fit(X_train, y_train)

xgb_pred = xgb.predict(X_test)
print("XGB Accuracy:", accuracy_score(y_test, xgb_pred))

# Save models
joblib.dump(rf, "rf_model.pkl")
joblib.dump(xgb, "xgb_model.pkl")

print("✅ Models trained & saved")