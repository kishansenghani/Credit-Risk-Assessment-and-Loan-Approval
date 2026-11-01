"""
utils/shap_explain.py
─────────────────────
Helper that wraps SHAP to produce per-feature importance values
for a single prediction row.
"""

import numpy as np

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False


def get_shap_explanation(model, features: np.ndarray, feature_names: list) -> dict:
    """
    Return a dict mapping feature name → SHAP value for the given input row.

    Falls back to a zeroed dict if SHAP is unavailable or the explainer fails.

    Parameters
    ----------
    model        : trained scikit-learn model (must expose predict_proba)
    features     : (1, n_features) numpy array – the encoded input row
    feature_names: ordered list of feature name strings

    Returns
    -------
    dict[str, float]
    """
    if not SHAP_AVAILABLE:
        return {name: 0.0 for name in feature_names}

    try:
        # TreeExplainer is fastest for tree-based models (RF, XGB, LightGBM).
        # Falls back to KernelExplainer for linear/other models.
        if hasattr(model, "estimators_") or hasattr(model, "feature_importances_"):
            explainer = shap.TreeExplainer(model)
            shap_vals = explainer.shap_values(features)
            # For binary classification TreeExplainer returns [class0, class1]
            if isinstance(shap_vals, list):
                vals = shap_vals[1][0]   # class 1 (Approved) shap values
            else:
                vals = shap_vals[0]
        else:
            # Kernel explainer – slow, but universal
            explainer = shap.KernelExplainer(
                model.predict_proba, shap.sample(features, 10)
            )
            shap_vals = explainer.shap_values(features, nsamples=50)
            vals = shap_vals[1][0] if isinstance(shap_vals, list) else shap_vals[0]

        return {name: round(float(val), 6) for name, val in zip(feature_names, vals)}

    except Exception as exc:
        # Non-fatal: return zeros so the rest of the API still works
        print(f"[SHAP] explanation failed: {exc}")
        return {name: 0.0 for name in feature_names}
