import joblib
import os

MODEL_DIR = os.path.dirname(__file__)

def load_model():
    try:
        model = joblib.load(os.path.join(MODEL_DIR, "loan_model.pkl"))
        scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
        feature_columns = joblib.load(os.path.join(MODEL_DIR, "feature_columns.pkl"))
        return model, scaler, feature_columns
    except FileNotFoundError:
        return None, None, None

LABEL_MAP = {0: "denied", 1: "review", 2: "approved"}

def predict_loan(features: dict) -> dict:
    model, scaler, feature_columns = load_model()
    if model is None:
        return {"success": False, "error": "ML model not trained yet."}

    # ── Auto-calculate anomaly feature ───────────────────────────
    emp_code = features.get("employment_type_encoded", 1)
    stability = features.get("stability_score", 0)
    high_risk_emp = emp_code <= 2  # freelancer, gig_worker, seasonal
    features["stability_anomaly"] = 1 if (high_risk_emp and stability >= 88) else 0

    feature_vector = [[features.get(col, 0) for col in feature_columns]]
    model_type = type(model).__name__

    if model_type == "LogisticRegression":
        fv_scaled = scaler.transform(feature_vector)
        prediction = model.predict(fv_scaled)[0]
        probabilities = model.predict_proba(fv_scaled)[0]
    else:
        prediction = model.predict(feature_vector)[0]
        probabilities = model.predict_proba(feature_vector)[0]

    return {
        "success": True,
        "ml_decision": LABEL_MAP[prediction],
        "model_type": model_type,
        "stability_anomaly_detected": bool(features["stability_anomaly"]),
        "confidence": {
            "denied":   round(float(probabilities[0]) * 100, 2),
            "review":   round(float(probabilities[1]) * 100, 2),
            "approved": round(float(probabilities[2]) * 100, 2)
        },
        "confidence_in_decision": round(float(max(probabilities)) * 100, 2)
    }

def get_employment_encoding(employment_type: str) -> int:
    encoding = {
        "full_time": 4, "part_time": 3,
        "freelancer": 2, "gig_worker": 1, "seasonal": 1
    }
    return encoding.get(employment_type.lower(), 1)
