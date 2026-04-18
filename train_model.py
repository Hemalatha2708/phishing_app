import pandas as pd
import pickle
import logging
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
from features import extract_features
from config import config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==============================
# 1. Load Dataset
# ==============================
df = pd.read_csv("Test.csv")

# Clean data
df = df.dropna()
df = df.drop_duplicates()

logger.info(f"Dataset Loaded: {df.shape}")

# ==============================
# 2. Feature Extraction
# ==============================
# Apply features using centralized extract_features from features.py
X = df['URL'].apply(lambda url: extract_features(url)).tolist()
y = df['Label']

logger.info("Feature extraction completed!")

# ==============================
# 3. Train-Test Split
# ==============================

# ==============================
# 3. Train-Test Split
# ==============================
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ==============================
# 4. Random Forest Model
# ==============================
rf_model = RandomForestClassifier(
    n_estimators=150,
    random_state=42,
    n_jobs=-1
)

rf_model.fit(X_train, y_train)
rf_pred = rf_model.predict(X_test)

rf_acc = accuracy_score(y_test, rf_pred)
logger.info(f"Random Forest Accuracy: {rf_acc:.4f}")

# ==============================
# 5. XGBoost Model
# ==============================
xgb_model = XGBClassifier(
    n_estimators=150,
    learning_rate=0.1,
    max_depth=6,
    eval_metric='logloss'
)

xgb_model.fit(X_train, y_train)
xgb_pred = xgb_model.predict(X_test)

xgb_acc = accuracy_score(y_test, xgb_pred)
logger.info(f"XGBoost Accuracy: {xgb_acc:.4f}")

# ==============================
# 6. Compare Models
# ==============================
best_model = "XGBoost" if xgb_acc > rf_acc else "Random Forest"
logger.info(f"Best Model: {best_model}")

# ==============================
# 7. Save Models
# ==============================
try:
    pickle.dump(rf_model, open(config.MODEL_PATH_RF, "wb"))
    pickle.dump(xgb_model, open(config.MODEL_PATH_XGB, "wb"))
    logger.info("Both models saved successfully!")
except Exception as e:
    logger.error(f"Error saving models: {str(e)}")