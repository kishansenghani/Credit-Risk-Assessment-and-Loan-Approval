import os
import joblib
import numpy as np
from flask import Blueprint, request, jsonify
from utils.shap_explain import get_shap_explanation
import datetime

predict_bp = Blueprint("predict", __name__)

# ---------------------------------------------------------------------------
# Model loading (lazy – loaded once on first request)
# ---------------------------------------------------------------------------
_model = None
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "model.pkl")


def _load_model():
    global _model
    if _model is None:
        if os.path.exists(MODEL_PATH):
            _model = joblib.load(MODEL_PATH)
        else:
            _model = None  # Model not trained yet
    return _model


# ---------------------------------------------------------------------------
# Application DB model (shared across routes)
# ---------------------------------------------------------------------------
from database import db


class LoanApplication(db.Model):
    __tablename__ = "loan_applications"
    id                 = db.Column(db.Integer, primary_key=True)
    applicant_name     = db.Column(db.String(120))
    applicant_income   = db.Column(db.Float)
    coapplicant_income = db.Column(db.Float)
    loan_amount        = db.Column(db.Float)
    loan_term          = db.Column(db.Float)
    credit_history     = db.Column(db.Float)
    gender             = db.Column(db.String(10))
    married            = db.Column(db.String(5))
    dependents         = db.Column(db.String(5))
    education          = db.Column(db.String(20))
    self_employed      = db.Column(db.String(5))
    property_area      = db.Column(db.String(20))
    prediction         = db.Column(db.String(20))   # "Approved" | "Rejected"
    confidence         = db.Column(db.Float)
    # ── NEW ─────────────────────────────────────────────────────────────────
    risk_band          = db.Column(db.String(10))   # "Low" | "Medium" | "High"
    top_shap_json      = db.Column(db.Text)         # JSON string of top-3 features
    # ────────────────────────────────────────────────────────────────────────
    submitted_at       = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        import json
        return {
            "id":                 self.id,
            "applicant_name":     self.applicant_name,
            "applicant_income":   self.applicant_income,
            "coapplicant_income": self.coapplicant_income,
            "loan_amount":        self.loan_amount,
            "loan_term":          self.loan_term,
            "credit_history":     self.credit_history,
            "gender":             self.gender,
            "married":            self.married,
            "dependents":         self.dependents,
            "education":          self.education,
            "self_employed":      self.self_employed,
            "property_area":      self.property_area,
            "prediction":         self.prediction,
            "confidence":         self.confidence,
            "risk_band":          self.risk_band,
            "top_shap":           json.loads(self.top_shap_json) if self.top_shap_json else [],
            "submitted_at":       self.submitted_at.isoformat() if self.submitted_at else None,
        }


# ---------------------------------------------------------------------------
# Feature engineering and encoding helper (aligned with trained XGBoost model)
# ---------------------------------------------------------------------------
FEATURE_COLUMNS = [
    "ApplicantIncome",
    "CoapplicantIncome",
    "LoanAmount",
    "Loan_Amount_Term",
    "Credit_History",
    "TotalIncome",
    "Debt_to_Income",
    "Loan_to_Income",
    "Gender_Male",
    "Married_Yes",
    "Dependents_1",
    "Dependents_2",
    "Dependents_3+",
    "Education_Not Graduate",
    "Self_Employed_Yes",
    "Property_Area_Semiurban",
    "Property_Area_Urban",
]


def _encode_features(data: dict):
    """
    Transforms applicant JSON into a 17-feature array/DataFrame matching
    the trained XGBoost model schema.
    """
    import pandas as pd

    def _get(key, default=0.0):
        val = data.get(key)
        if val is None:
            val = data.get(key.lower())
        if val is None or val == "":
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    def _get_str(key, default=""):
        val = data.get(key)
        if val is None:
            val = data.get(key.lower())
        return str(val).strip() if val is not None else default

    app_inc  = _get("ApplicantIncome", 0.0)
    coapp_inc = _get("CoapplicantIncome", 0.0)
    total_inc = app_inc + coapp_inc
    amt      = _get("LoanAmount", 128.0)        # median default
    term     = _get("Loan_Amount_Term", 360.0)  # mode default
    credit   = _get("Credit_History", 1.0)      # median/mode default

    # Engineered features
    dti = (amt * 1000.0 / term) / (total_inc + 1e-5)
    lti = (amt * 1000.0) / (total_inc + 1e-5)

    gender   = _get_str("Gender", "Male")
    married  = _get_str("Married", "No")
    dep      = _get_str("Dependents", "0")
    edu      = _get_str("Education", "Graduate")
    self_emp = _get_str("Self_Employed", "No")
    area     = _get_str("Property_Area", "Urban")

    row = {
        "ApplicantIncome":         app_inc,
        "CoapplicantIncome":       coapp_inc,
        "LoanAmount":              amt,
        "Loan_Amount_Term":        term,
        "Credit_History":          credit,
        "TotalIncome":             total_inc,
        "Debt_to_Income":          dti,
        "Loan_to_Income":          lti,
        "Gender_Male":             1 if gender.lower() == "male" else 0,
        "Married_Yes":             1 if married.lower() == "yes" else 0,
        "Dependents_1":            1 if dep == "1" else 0,
        "Dependents_2":            1 if dep == "2" else 0,
        "Dependents_3+":           1 if dep in ["3", "3+"] else 0,
        "Education_Not Graduate":  1 if edu.lower() in ["not graduate", "not_graduate"] else 0,
        "Self_Employed_Yes":       1 if self_emp.lower() == "yes" else 0,
        "Property_Area_Semiurban": 1 if area.lower() == "semiurban" else 0,
        "Property_Area_Urban":     1 if area.lower() == "urban" else 0,
    }

    df_row = pd.DataFrame([row])[FEATURE_COLUMNS]
    return df_row



def _compute_risk_band(approve_prob: float) -> str:
    """
    Map approval probability to a risk band.
      approve_prob >= 0.70  →  Low risk    (likely approved)
      approve_prob >= 0.45  →  Medium risk
      approve_prob <  0.45  →  High risk   (likely rejected)
    """
    if approve_prob >= 0.70:
        return "Low"
    elif approve_prob >= 0.45:
        return "Medium"
    return "High"


def _top3_shap(shap_dict: dict) -> list:
    """Return top-3 features by absolute SHAP value as [{feature, value, direction}]."""
    entries = sorted(
        shap_dict.items(),
        key=lambda kv: abs(kv[1]),
        reverse=True,
    )[:3]
    return [
        {
            "feature":   feat,
            "value":     round(val, 6),
            "direction": "positive" if val >= 0 else "negative",
        }
        for feat, val in entries
    ]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@predict_bp.route("/predict", methods=["POST"])
def predict():
    """POST /api/predict — run the loan approval model and return prediction + SHAP."""
    data = request.get_json(silent=True) or {}

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    model = _load_model()
    if model is None:
        # ── Mock response when model.pkl is not yet trained ──────────────────
        mock_shap = {
            "Credit_History":    0.35,
            "ApplicantIncome":   0.18,
            "LoanAmount":       -0.12,
            "Loan_Amount_Term":  0.07,
            "Property_Area":     0.05,
        }
        return jsonify({
            "prediction":  "Approved",
            "confidence":  0.82,
            "risk_band":   "Low",
            "label":       1,
            "top_shap":    _top3_shap(mock_shap),
            "shap_values": mock_shap,
            "note":        "Mock response – train and save a model to models/model.pkl",
        }), 200

    try:
        features      = _encode_features(data)
        prob          = model.predict_proba(features)[0]
        approve_prob  = float(prob[1]) if len(prob) > 1 else float(prob[0])
        label         = int(np.argmax(prob))
        confidence    = float(prob[label])
        prediction    = "Approved" if label == 1 else "Rejected"
        risk_band     = _compute_risk_band(approve_prob)

        # ── SHAP explanation ─────────────────────────────────────────────────
        shap_dict  = get_shap_explanation(model, features, FEATURE_COLUMNS)
        top_shap   = _top3_shap(shap_dict)

        # ── Persist to DB ────────────────────────────────────────────────────
        import json
        app_record = LoanApplication(
            applicant_name     = data.get("applicant_name", "Anonymous"),
            applicant_income   = data.get("ApplicantIncome"),
            coapplicant_income = data.get("CoapplicantIncome"),
            loan_amount        = data.get("LoanAmount"),
            loan_term          = data.get("Loan_Amount_Term"),
            credit_history     = data.get("Credit_History"),
            gender             = data.get("Gender"),
            married            = data.get("Married"),
            dependents         = data.get("Dependents"),
            education          = data.get("Education"),
            self_employed      = data.get("Self_Employed"),
            property_area      = data.get("Property_Area"),
            prediction         = prediction,
            confidence         = confidence,
            risk_band          = risk_band,
            top_shap_json      = json.dumps(top_shap),
        )
        db.session.add(app_record)
        db.session.commit()

        return jsonify({
            "id":          app_record.id,
            "prediction":  prediction,
            "confidence":  confidence,
            "risk_band":   risk_band,
            "label":       label,
            "top_shap":    top_shap,
            "shap_values": shap_dict,
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
