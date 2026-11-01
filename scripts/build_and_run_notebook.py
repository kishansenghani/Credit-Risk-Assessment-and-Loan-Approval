"""
scripts/build_and_run_notebook.py
─────────────────────────────────
Constructs the complete 02_model_training.ipynb notebook using nbformat,
trains Logistic Regression, Decision Tree, Random Forest, and XGBoost,
generates a comprehensive 4-model comparison table, and fine-tunes XGBoost.
Executes the notebook via nbconvert so all outputs and charts are embedded.
"""

from pathlib import Path
import nbformat as nbf
import subprocess
import sys

PROJECT_ROOT = Path("e:/Loan_Risk_Analysis")
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
MODELS_DIR = PROJECT_ROOT / "backend" / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3"
    },
    "language_info": {
        "name": "python",
        "version": "3.13"
    }
}

cells = []

# ── Cell 1: Markdown Title ───────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""# 🏦 Loan Approval & Credit Risk Analysis: End-to-End ML Training Pipeline

This notebook implements the complete machine learning workflow for predicting loan approval and credit risk:
1. **Data Ingestion**: Load dataset from `data/loan_data.csv`
2. **Preprocessing**: Encode target (`Loan_Status`), impute missing values (median for numerics, mode for categoricals)
3. **Feature Engineering**: Compute `TotalIncome`, `Debt_to_Income` ratio, and `Loan_to_Income` ratio
4. **Encoding**: One-hot encode categorical features
5. **Stratified Split**: 80/20 train/test split stratified on target
6. **Class Balancing**: Apply **SMOTE** on the training set only
7. **Model Benchmarking**: Train and compare **Logistic Regression**, **Decision Tree**, **Random Forest**, and **XGBoost**
8. **Model Comparison Table**: Compare all 4 models across Accuracy, Precision, Recall, F1, and ROC-AUC
9. **XGBoost Fine-Tuning**: Optimize the champion XGBoost classifier with **GridSearchCV**
10. **Test Set Evaluation**: Confusion Matrix heatmap, ROC Curve, and classification report
11. **Artifacts Export**: Save trained model to `backend/models/model.pkl` and 100-row pre-SMOTE background sample to `backend/models/background_data.csv`
12. **SHAP Explainability**: SHAP TreeExplainer feature importance and local waterfall analysis
"""))

# ── Cell 2: Imports ──────────────────────────────────────────────────────────
cells.append(nbf.v4.new_code_cell("""# ── Environment & Library Imports ──────────────────────────────────────────
import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report, roc_curve
)
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier
import shap

# Set visual styling
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.figsize"] = (8, 5)
plt.rcParams["font.size"] = 10

print("All required packages successfully imported.")
"""))

# ── Cell 3: Step 1 Markdown ──────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""## 1. Data Ingestion & Initial Inspection

We load the loan dataset from `data/loan_data.csv` and inspect its shape, columns, and initial null values.
"""))

# ── Cell 4: Step 1 Code ──────────────────────────────────────────────────────
cells.append(nbf.v4.new_code_cell("""data_path = os.path.join("..", "data", "loan_data.csv")
if not os.path.exists(data_path):
    data_path = os.path.join("data", "loan_data.csv")

df = pd.read_csv(data_path)
print(f"Dataset Shape: {df.shape[0]} rows × {df.shape[1]} columns")

# Drop Loan_ID identifier as it carries no predictive value
if "Loan_ID" in df.columns:
    df = df.drop(columns=["Loan_ID"])

df.head()
"""))

# ── Cell 5: Step 2 Markdown ──────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""## 2. Target Encoding & Missing Value Imputation

- **Target Encoding**: `Loan_Status` (`Y` → `1`, `N` → `0`)
- **Numeric Imputation (Median)**: `LoanAmount`, `Credit_History`
- **Categorical Imputation (Mode)**: `Gender`, `Married`, `Self_Employed`, `Dependents`, `Loan_Amount_Term`, `Property_Area`
"""))

# ── Cell 6: Step 2 Code ──────────────────────────────────────────────────────
cells.append(nbf.v4.new_code_cell("""# 1. Target Encoding
df["Loan_Status"] = df["Loan_Status"].map({"Y": 1, "N": 0})

print("Target Class Distribution:")
print(df["Loan_Status"].value_counts(normalize=True).rename({1: "Approved (Y)", 0: "Rejected (N)"}))

# 2. Impute Numeric columns with Median
numeric_cols = ["LoanAmount", "Credit_History"]
for col in numeric_cols:
    median_val = df[col].median()
    df[col] = df[col].fillna(median_val)
    print(f"Imputed numeric {col} with median: {median_val}")

# 3. Impute Categorical columns with Mode
categorical_cols = ["Gender", "Married", "Dependents", "Education", "Self_Employed", "Loan_Amount_Term", "Property_Area"]
for col in categorical_cols:
    mode_val = df[col].mode()[0]
    df[col] = df[col].fillna(mode_val)
    print(f"Imputed categorical {col} with mode: {mode_val}")

# Verify no missing values remain
print(f"\\nRemaining null values across dataset: {df.isnull().sum().sum()}")
"""))

# ── Cell 7: Step 3 Markdown ──────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""## 3. Feature Engineering

We engineer three key financial domain features:
1. **TotalIncome**: Combined applicant and co-applicant monthly earnings.
   $$\\text{TotalIncome} = \\text{ApplicantIncome} + \\text{CoapplicantIncome}$$
2. **Debt_to_Income**: Estimated monthly debt service (EMI) divided by total income.
   $$\\text{Debt\\_to\\_Income} = \\frac{\\text{LoanAmount} \\times 1000 / \\text{Loan\\_Amount\\_Term}}{\\text{TotalIncome} + \\epsilon}$$
3. **Loan_to_Income**: Total loan requested relative to monthly total income.
   $$\\text{Loan\\_to\\_Income} = \\frac{\\text{LoanAmount} \\times 1000}{\\text{TotalIncome} + \\epsilon}$$
"""))

# ── Cell 8: Step 3 Code ──────────────────────────────────────────────────────
cells.append(nbf.v4.new_code_cell("""# Calculate engineered features
df["TotalIncome"] = df["ApplicantIncome"] + df["CoapplicantIncome"]

# Debt to income: (LoanAmount in thousands * 1000 / term in months) / TotalIncome
df["Debt_to_Income"] = (df["LoanAmount"] * 1000.0 / df["Loan_Amount_Term"]) / (df["TotalIncome"] + 1e-5)

# Loan to income: (LoanAmount in thousands * 1000) / TotalIncome
df["Loan_to_Income"] = (df["LoanAmount"] * 1000.0) / (df["TotalIncome"] + 1e-5)

print("Engineered Features Summary:")
display(df[["ApplicantIncome", "CoapplicantIncome", "TotalIncome", "LoanAmount", "Loan_Amount_Term", "Debt_to_Income", "Loan_to_Income"]].describe())
"""))

# ── Cell 9: Step 4 Markdown ──────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""## 4. One-Hot Encoding Categorical Variables

We one-hot encode all categorical variables (`Gender`, `Married`, `Dependents`, `Education`, `Self_Employed`, `Property_Area`) with `drop_first=True` to prevent multicollinearity.
"""))

# ── Cell 10: Step 4 Code ─────────────────────────────────────────────────────
cells.append(nbf.v4.new_code_cell("""ohe_cols = ["Gender", "Married", "Dependents", "Education", "Self_Employed", "Property_Area"]
df_encoded = pd.get_dummies(df, columns=ohe_cols, drop_first=True, dtype=int)

X = df_encoded.drop(columns=["Loan_Status"])
y = df_encoded["Loan_Status"]

feature_columns = list(X.columns)
print(f"Final Feature Matrix: {X.shape[0]} rows × {X.shape[1]} features")
print(f"\\nFeature list ({len(feature_columns)}):\\n{feature_columns}")
"""))

# ── Cell 11: Step 5 Markdown ─────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""## 5. Stratified 80/20 Train / Test Split

We split into 80% training and 20% testing data, stratifying on `y` (`Loan_Status`) to preserve the target class ratio in both splits.
"""))

# ── Cell 12: Step 5 Code ─────────────────────────────────────────────────────
cells.append(nbf.v4.new_code_cell("""X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print(f"Training set: {X_train.shape[0]} samples")
print(f"Testing set : {X_test.shape[0]} samples")
print(f"Train Approval Rate: {y_train.mean():.2%}")
print(f"Test Approval Rate : {y_test.mean():.2%}")
"""))

# ── Cell 13: Step 6 Markdown ─────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""## 6. Class Imbalance Handling via SMOTE (Training Set Only)

To prevent data leakage, **SMOTE** (Synthetic Minority Over-sampling Technique) is applied **strictly to the training set**. The test set remains untouched to accurately reflect real-world distributions.
"""))

# ── Cell 14: Step 6 Code ─────────────────────────────────────────────────────
cells.append(nbf.v4.new_code_cell("""print(f"Before SMOTE - Training Class Counts:\\n{y_train.value_counts().to_dict()}")

smote = SMOTE(random_state=42)
X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

print(f"\\nAfter SMOTE  - Balanced Training Class Counts:\\n{pd.Series(y_train_res).value_counts().to_dict()}")
print(f"Balanced Training Matrix Shape: {X_train_res.shape}")
"""))

# ── Cell 15: Step 7 Markdown: 4 Models Benchmark ─────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""## 7. Multi-Model Benchmark: Logistic Regression, Decision Tree, Random Forest & XGBoost

We train four distinct model families on the exact same SMOTE-balanced training set and evaluate them on the identical unseen test set:
1. **Logistic Regression**: Linear baseline with `StandardScaler` feature normalization.
2. **Decision Tree**: Non-linear, interpretable single-tree classifier (`max_depth=4`).
3. **Random Forest**: Bagging ensemble of 100 de-correlated decision trees.
4. **XGBoost**: Gradient boosting decision trees combining weak learners iteratively.
"""))

# ── Cell 16: Step 7 Code: Train and Benchmark 4 Models ───────────────────────
cells.append(nbf.v4.new_code_cell("""# Define all 4 candidate models
candidate_models = {
    "Logistic Regression": Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=1000, random_state=42))
    ]),
    "Decision Tree": DecisionTreeClassifier(
        max_depth=4,
        min_samples_split=10,
        random_state=42
    ),
    "Random Forest": RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42
    ),
    "XGBoost (Default)": XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.05,
        random_state=42,
        eval_metric="logloss"
    )
}

# Train and evaluate all 4 models
benchmark_results = []
trained_candidates = {}

for name, model in candidate_models.items():
    model.fit(X_train_res, y_train_res)
    trained_candidates[name] = model
    
    y_pred_m = model.predict(X_test)
    y_prob_m = model.predict_proba(X_test)[:, 1]
    
    benchmark_results.append({
        "Model": name,
        "Accuracy": accuracy_score(y_test, y_pred_m),
        "Precision": precision_score(y_test, y_pred_m),
        "Recall": recall_score(y_test, y_pred_m),
        "F1-Score": f1_score(y_test, y_pred_m),
        "ROC-AUC": roc_auc_score(y_test, y_prob_m)
    })

comparison_df = pd.DataFrame(benchmark_results)
"""))

# ── Cell 17: Step 8 Markdown: Comparison Table ───────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""## 8. Model Performance Comparison Table

Here is the comparative performance across all four models on the unseen holdout test set:
"""))

# ── Cell 18: Step 8 Code: Comparison Table & Plot ────────────────────────────
cells.append(nbf.v4.new_code_cell("""# Format and display the comparison table
display_table = comparison_df.copy()
for metric in ["Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC"]:
    display_table[metric] = display_table[metric].apply(lambda x: f"{x * 100:.2f}%" if metric != "ROC-AUC" else f"{x:.4f}")

print("=====================================================================")
print("          MODEL PERFORMANCE COMPARISON (TEST SET)")
print("=====================================================================")
display(display_table)

# Visual comparison bar chart
metrics_to_plot = ["Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC"]
plot_df = comparison_df.melt(id_vars="Model", value_vars=metrics_to_plot, var_name="Metric", value_name="Score")

plt.figure(figsize=(12, 6))
chart = sns.barplot(data=plot_df, x="Metric", y="Score", hue="Model", palette="Set2")
plt.title("4-Model Performance Comparison (Test Set)", fontsize=13, fontweight="bold", pad=12)
plt.ylabel("Score")
plt.ylim(0.70, 1.0)
plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0.)

for p in chart.patches:
    h = p.get_height()
    if h > 0:
        chart.annotate(f"{h:.2f}",
                       (p.get_x() + p.get_width() / 2., h),
                       ha='center', va='bottom', fontsize=8, rotation=0, xytext=(0, 2),
                       textcoords='offset points')

plt.tight_layout()
plt.show()
"""))

# ── Cell 19: Step 9 Markdown: XGBoost Grid Search ────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""## 9. Final XGBoost Classifier Hyperparameter Grid Search

XGBoost is selected for production deployment because of its exceptional handling of tabular feature interactions, gradient boosting efficiency, and direct integration with **TreeSHAP** for local/global explainability.

We perform 5-fold cross-validation over:
- `n_estimators`: `[50, 100, 150]`
- `max_depth`: `[3, 4, 5]`
- `learning_rate`: `[0.01, 0.05, 0.1]`
"""))

# ── Cell 20: Step 9 Code: XGBoost Grid Search ────────────────────────────────
cells.append(nbf.v4.new_code_cell("""param_grid = {
    "n_estimators": [50, 100, 150],
    "max_depth": [3, 4, 5],
    "learning_rate": [0.01, 0.05, 0.1],
}

xgb_base = XGBClassifier(
    random_state=42,
    eval_metric="logloss"
)

grid_search = GridSearchCV(
    estimator=xgb_base,
    param_grid=param_grid,
    cv=5,
    scoring="roc_auc",
    n_jobs=1,
    verbose=1
)

grid_search.fit(X_train_res, y_train_res)

best_model = grid_search.best_estimator_
print(f"\\nBest Hyperparameters: {grid_search.best_params_}")
print(f"Best 5-Fold Cross-Validated ROC-AUC: {grid_search.best_score_:.4f}")
"""))

# ── Cell 21: Step 10 Markdown: Evaluation ────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""## 10. Final XGBoost Test Set Evaluation & Diagnostics

Detailed evaluation of the tuned champion model on the unseen test set:
- **Confusion Matrix**
- **ROC-AUC Curve**
- **Full Classification Report**
"""))

# ── Cell 22: Step 10 Code: Evaluation ────────────────────────────────────────
cells.append(nbf.v4.new_code_cell("""y_pred = best_model.predict(X_test)
y_prob = best_model.predict_proba(X_test)[:, 1]

acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
roc = roc_auc_score(y_test, y_prob)
cm = confusion_matrix(y_test, y_pred)

print("=" * 45)
print("FINAL XGBOOST TEST SET METRICS")
print("=" * 45)
print(f"  Accuracy : {acc * 100:.2f}%")
print(f"  Precision: {prec * 100:.2f}%")
print(f"  Recall   : {rec * 100:.2f}%")
print(f"  F1-Score : {f1 * 100:.2f}%")
print(f"  ROC-AUC  : {roc:.4f}")
print("=" * 45)

print("\\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["Rejected (0)", "Approved (1)"]))

# Plot Confusion Matrix and ROC Curve
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Confusion Matrix
sns.heatmap(
    cm, annot=True, fmt="d", cmap="Blues", cbar=False, ax=axes[0],
    xticklabels=["Predicted Rejected", "Predicted Approved"],
    yticklabels=["Actual Rejected", "Actual Approved"]
)
axes[0].set_title("Confusion Matrix (Test Set)", fontsize=12, fontweight="bold")

# ROC Curve
fpr, tpr, _ = roc_curve(y_test, y_prob)
axes[1].plot(fpr, tpr, color="#2563eb", lw=2.5, label=f"XGBoost (AUC = {roc:.3f})")
axes[1].plot([0, 1], [0, 1], color="#94a3b8", linestyle="--")
axes[1].set_xlabel("False Positive Rate")
axes[1].set_ylabel("True Positive Rate")
axes[1].set_title("ROC-AUC Curve", fontsize=12, fontweight="bold")
axes[1].legend(loc="lower right")

plt.tight_layout()
plt.show()
"""))

# ── Cell 23: Step 11 Markdown: Model Saving ──────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""## 11. Save Model & Pre-SMOTE Background Sample

We persist the trained model and feature metadata:
1. `backend/models/model.pkl`: Best trained XGBoost model using `joblib`.
2. `backend/models/background_data.csv`: 100-row random sample of **real, pre-SMOTE** training features for SHAP background reference.
3. `backend/models/feature_columns.json`: The exact feature column order required by the inference API.
"""))

# ── Cell 24: Step 11 Code: Model Saving ──────────────────────────────────────
cells.append(nbf.v4.new_code_cell("""backend_models_dir = os.path.join("..", "backend", "models")
if not os.path.exists(backend_models_dir):
    backend_models_dir = os.path.join("backend", "models")
os.makedirs(backend_models_dir, exist_ok=True)

# 1. Save Trained Model
model_save_path = os.path.join(backend_models_dir, "model.pkl")
joblib.dump(best_model, model_save_path)
print(f"Trained model saved to: {model_save_path}")

# Also copy to root models/
root_models_dir = os.path.join("..", "models") if os.path.exists(os.path.join("..", "models")) else "models"
if os.path.exists(root_models_dir):
    joblib.dump(best_model, os.path.join(root_models_dir, "model.pkl"))

# 2. Save 100-row pre-SMOTE background sample for SHAP
sample_size = min(100, len(X_train))
background_sample = X_train.sample(n=sample_size, random_state=42)
bg_save_path = os.path.join(backend_models_dir, "background_data.csv")
background_sample.to_csv(bg_save_path, index=False)
print(f"SHAP background data ({sample_size} rows) saved to: {bg_save_path}")

# 3. Save feature column order
feature_cols_path = os.path.join(backend_models_dir, "feature_columns.json")
with open(feature_cols_path, "w") as f:
    json.dump(feature_columns, f, indent=2)
print(f"Feature columns ({len(feature_columns)}) saved to: {feature_cols_path}")
"""))

# ── Cell 25: Step 12 Markdown: SHAP ──────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""## 12. SHAP Explainability Verification

Using `shap.TreeExplainer` on the trained XGBoost model and the 100-row background dataset:
- We compute SHAP values for the test set.
- We plot global feature importance (SHAP Summary Beeswarm Plot).
- We inspect a single prediction's waterfall plot to demonstrate how feature contributions drive decisions.
"""))

# ── Cell 26: Step 12 Code: SHAP ──────────────────────────────────────────────
cells.append(nbf.v4.new_code_cell("""explainer = shap.TreeExplainer(best_model, data=background_sample)
shap_values = explainer(X_test)

plt.figure(figsize=(9, 6))
shap.plots.beeswarm(shap_values, max_display=12, show=False)
plt.title("SHAP Beeswarm Summary Plot (Test Set)", fontsize=12, fontweight="bold")
plt.tight_layout()
plt.show()

# Local Waterfall Plot for the first test instance
plt.figure(figsize=(8, 5))
shap.plots.waterfall(shap_values[0], show=False)
plt.title(f"SHAP Waterfall Explanation (Instance #0: Actual={y_test.iloc[0]}, Pred={y_pred[0]})", fontsize=11, fontweight="bold")
plt.tight_layout()
plt.show()

print("Complete pipeline executed successfully!")
"""))

nb.cells = cells

# Save the unexecuted notebook
output_nb_path = NOTEBOOKS_DIR / "02_model_training.ipynb"
with open(output_nb_path, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"Notebook written to {output_nb_path}")

# Execute via nbconvert
print("Executing notebook via nbconvert...")
res = subprocess.run([
    sys.executable, "-m", "jupyter", "nbconvert",
    "--to", "notebook",
    "--execute", str(output_nb_path),
    "--output", "02_model_training.ipynb",
    "--ExecutePreprocessor.timeout=300"
], capture_output=True, text=True)

if res.returncode == 0:
    print("[OK] Notebook successfully executed and rendered!")
else:
    print("Execution output:")
    print(res.stdout)
    print("Execution error:")
    print(res.stderr)
