import joblib

rf = joblib.load("rf_model.pkl")
xgb = joblib.load("xgb_model.pkl")

def predict(features):
    # Get probabilities from both models
    rf_prob = rf.predict_proba([features])[0][1]
    xgb_prob = xgb.predict_proba([features])[0][1]

    # Average probability → risk score
    risk_score = ((rf_prob + xgb_prob) / 2) * 100

    # Final label
    result = "PHISHING ⚠️" if risk_score > 50 else "SAFE ✅"

    return result, round(risk_score, 2)