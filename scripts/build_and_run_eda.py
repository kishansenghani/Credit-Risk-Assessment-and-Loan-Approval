"""
scripts/build_and_run_eda.py
────────────────────────────
Constructs notebooks/01_eda.ipynb using nbformat and executes it via nbconvert
so all visualizations, statistics, and findings are pre-rendered in the notebook.
"""

from pathlib import Path
import nbformat as nbf
import subprocess
import sys

PROJECT_ROOT = Path("e:/Loan_Risk_Analysis")
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)

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

# ── Cell 1: Header Markdown ──────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""# 📊 Exploratory Data Analysis (EDA): Loan Risk & Approval Prediction

### Objective
This notebook conducts comprehensive exploratory data analysis on the **Loan Risk Analysis** dataset to understand borrower demographics, financial characteristics, risk factors, and their direct relationship to loan approval (`Loan_Status`).

### Key Analysis Sections
1. **Target Class Balance**: Distribution of Approved (`Y`) vs Rejected (`N`) loans.
2. **Approval Rates by Categorical Drivers**: Approval rate by `Credit_History`, `Education`, `Property_Area`, and `Married`.
3. **Income & Loan Amount Distributions**: Distribution curves and outliers for `ApplicantIncome`, `CoapplicantIncome`, and `LoanAmount`.
4. **Correlation Analysis**: Correlation matrix and heatmap across all numerical features and target status.
5. **Key Takeaways & Modeling Strategy**: Strategic takeaways for feature engineering, class balancing, and model architecture.
"""))

# ── Cell 2: Imports ──────────────────────────────────────────────────────────
cells.append(nbf.v4.new_code_cell("""import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Visual styling configuration
sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams["figure.figsize"] = (9, 5)
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["axes.titleweight"] = "bold"

print("✅ Libraries loaded successfully.")
"""))

# ── Cell 3: Data Ingestion Markdown ──────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""## 1. Dataset Ingestion & Overview

Loading `data/loan_data.csv` and inspecting structure, dimensions, and missing values.
"""))

# ── Cell 4: Data Ingestion Code ──────────────────────────────────────────────
cells.append(nbf.v4.new_code_cell("""data_path = os.path.join("..", "data", "loan_data.csv")
if not os.path.exists(data_path):
    data_path = os.path.join("data", "loan_data.csv")

df = pd.read_csv(data_path)
print(f"Dataset Shape: {df.shape[0]} rows × {df.shape[1]} columns\\n")

# Drop Loan_ID identifier
if "Loan_ID" in df.columns:
    df = df.drop(columns=["Loan_ID"])

# Display schema information and sample records
display(df.head())
print("\\nMissing Value Counts:")
display(df.isnull().sum()[df.isnull().sum() > 0].to_frame(name="Missing Count"))
"""))

# ── Cell 5: Class Balance Markdown ───────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""## 2. Target Class Balance (`Loan_Status`)

Evaluating the distribution between approved (`Y`) and rejected (`N`) loan applications.
"""))

# ── Cell 6: Class Balance Code ───────────────────────────────────────────────
cells.append(nbf.v4.new_code_cell("""counts = df["Loan_Status"].value_counts()
pcts = df["Loan_Status"].value_counts(normalize=True) * 100

fig, ax = plt.subplots(figsize=(7, 4.5))
palette = ["#10b981", "#ef4444"]  # Green for Approved, Red for Rejected
bars = ax.bar(["Approved (Y)", "Rejected (N)"], [counts.get("Y", 0), counts.get("N", 0)], color=palette, width=0.45, edgecolor="#1e293b", linewidth=1.2)

for bar in bars:
    height = bar.get_height()
    pct = (height / len(df)) * 100
    ax.annotate(f"{height}\\n({pct:.1f}%)",
                xy=(bar.get_x() + bar.get_width() / 2, height / 2),
                xytext=(0, 0), textcoords="offset points",
                ha="center", va="center", color="white", fontweight="bold", fontsize=11)

ax.set_title("Loan Status Class Balance", pad=15)
ax.set_ylabel("Number of Applications")
ax.set_ylim(0, max(counts) * 1.15)
plt.tight_layout()
plt.show()

print(f"Total Applications: {len(df)}")
print(f"Approved: {counts.get('Y', 0)} ({pcts.get('Y', 0):.2f}%)")
print(f"Rejected: {counts.get('N', 0)} ({pcts.get('N', 0):.2f}%)")
"""))

# ── Cell 7: Class Balance Markdown Findings ──────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""### 💡 Finding 1: Target Class Imbalance
- **Approved Applications (`Y`)**: 422 (68.73%)
- **Rejected Applications (`N`)**: 192 (31.27%)
- **Impact on Modeling**: A naive baseline predicting all loans as "Approved" would achieve ~68.7% accuracy while completely failing to identify risky applicants.
- **Strategic Decision**: Synthetic Minority Over-sampling Technique (**SMOTE**) is necessary on the training split to teach the model decision boundaries for rejections, alongside tracking **Precision**, **Recall**, and **ROC-AUC** rather than raw accuracy.
"""))

# ── Cell 8: Approval Rates Markdown ──────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""## 3. Approval Rate by Key Demographics & Credit Factors

Analyzing approval rates across:
1. **Credit_History**: Past credit record (1.0 = cleared debt, 0.0 = defaulted).
2. **Education**: Graduate vs. Not Graduate.
3. **Property_Area**: Semiurban, Urban, and Rural locations.
4. **Married**: Married vs. Single status.
"""))

# ── Cell 9: Approval Rates Code ──────────────────────────────────────────────
cells.append(nbf.v4.new_code_cell("""# Helper function to compute approval rate
def get_approval_df(col_name):
    temp = df.dropna(subset=[col_name]).copy()
    grouped = temp.groupby(col_name)["Loan_Status"].agg(
        Total="count",
        Approved=lambda x: (x == "Y").sum()
    ).reset_index()
    grouped["ApprovalRate"] = (grouped["Approved"] / grouped["Total"]) * 100
    return grouped

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
features = [
    ("Credit_History", "Approval Rate by Credit History", axes[0, 0]),
    ("Education", "Approval Rate by Education", axes[0, 1]),
    ("Property_Area", "Approval Rate by Property Area", axes[1, 0]),
    ("Married", "Approval Rate by Marital Status", axes[1, 1])
]

color_theme = ["#3b82f6", "#6366f1", "#8b5cf6"]

for col, title, ax in features:
    data = get_approval_df(col)
    # Format labels if numeric
    if col == "Credit_History":
        data[col] = data[col].map({1.0: "Good (1.0)", 0.0: "Bad (0.0)"})
    
    bars = ax.bar(data[col].astype(str), data["ApprovalRate"], color=color_theme[:len(data)], width=0.5, edgecolor="#334155")
    
    for bar, (_, row) in zip(bars, data.iterrows()):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 2,
                f"{h:.1f}%\\n({int(row['Approved'])}/{int(row['Total'])})",
                ha="center", va="bottom", fontsize=10, fontweight="bold")
    
    ax.set_title(title, pad=12)
    ax.set_ylabel("Approval Rate (%)")
    ax.set_ylim(0, 105)
    ax.axhline(68.7, color="#ef4444", linestyle="--", alpha=0.6, label="Overall Avg (68.7%)")
    ax.legend(loc="upper left", framealpha=0.8)

plt.tight_layout()
plt.show()

# Display tabular rates
for col, title, _ in features:
    print(f"--- {title} ---")
    display(get_approval_df(col))
"""))

# ── Cell 10: Approval Rates Markdown Findings ────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""### 💡 Finding 2: Approval Driver Insights
1. **Credit History is the Dominant Factor**:
   - Applicants with good credit history (`1.0`) have an approval rate of **79.58%** (378 / 475).
   - Applicants with poor credit history (`0.0`) have an approval rate of only **7.87%** (7 / 89).
   - A favorable credit history multiplies approval chances by over **10×**.

2. **Education Matters**:
   - Graduates have a **70.83%** approval rate versus **61.19%** for non-graduates.

3. **Property Area Disparities**:
   - **Semiurban** properties exhibit the highest approval rate at **76.82%** (well above average).
   - **Urban** properties stand at **65.84%**.
   - **Rural** properties have the lowest approval rate at **61.45%**.

4. **Marital Status Advantage**:
   - Married applicants have a **71.62%** approval rate compared to **62.91%** for unmarried applicants, likely driven by dual household income support.
"""))

# ── Cell 11: Income & Loan Amount Distributions Markdown ─────────────────────
cells.append(nbf.v4.new_markdown_cell("""## 4. Income and Loan Amount Distributions

Inspecting the spread, skewness, and extreme values for `ApplicantIncome`, `CoapplicantIncome`, `TotalIncome`, and `LoanAmount`.
"""))

# ── Cell 12: Income & Loan Amount Code ───────────────────────────────────────
cells.append(nbf.v4.new_code_cell("""# Compute Total Income
df_clean = df.copy()
df_clean["TotalIncome"] = df_clean["ApplicantIncome"] + df_clean["CoapplicantIncome"]
df_clean["LoanAmount"] = df_clean["LoanAmount"].fillna(df_clean["LoanAmount"].median())

fig, axes = plt.subplots(2, 2, figsize=(14, 9))

# 1. ApplicantIncome
sns.histplot(df_clean["ApplicantIncome"], kde=True, ax=axes[0, 0], color="#0284c7", bins=30)
axes[0, 0].set_title("Applicant Income Distribution")
axes[0, 0].set_xlabel("Applicant Income (₹ / month)")

# 2. CoapplicantIncome
sns.histplot(df_clean[df_clean["CoapplicantIncome"] > 0]["CoapplicantIncome"], kde=True, ax=axes[0, 1], color="#0d9488", bins=30)
axes[0, 1].set_title("Coapplicant Income Distribution (Non-zero)")
axes[0, 1].set_xlabel("Coapplicant Income (₹ / month)")

# 3. TotalIncome
sns.histplot(df_clean["TotalIncome"], kde=True, ax=axes[1, 0], color="#7c3aed", bins=30)
axes[1, 0].set_title("Total Household Income Distribution")
axes[1, 0].set_xlabel("Total Income (₹ / month)")

# 4. LoanAmount
sns.histplot(df_clean["LoanAmount"], kde=True, ax=axes[1, 1], color="#e11d48", bins=30)
axes[1, 1].set_title("Loan Amount Distribution (in ₹000s)")
axes[1, 1].set_xlabel("Loan Amount (₹000)")

plt.tight_layout()
plt.show()

# Distribution summary statistics
stats = df_clean[["ApplicantIncome", "CoapplicantIncome", "TotalIncome", "LoanAmount"]].describe().T
stats["skewness"] = df_clean[["ApplicantIncome", "CoapplicantIncome", "TotalIncome", "LoanAmount"]].skew()
display(stats[["mean", "std", "min", "50%", "max", "skewness"]].rename(columns={"50%": "median"}))
"""))

# ── Cell 13: Income & Loan Amount Markdown Findings ──────────────────────────
cells.append(nbf.v4.new_markdown_cell("""### 💡 Finding 3: Financial Feature Characteristics & Outliers
1. **Severe Right Skewness**:
   - `ApplicantIncome` has a median of **₹3,812** but a maximum of **₹81,000** (skewness = +6.54).
   - `CoapplicantIncome` has over **44% zero values** (single-earner households).
   - `LoanAmount` has a median of **₹128,000** but extends up to **₹700,000** (skewness = +2.74).
2. **Modeling Implications**:
   - High positive skew and extreme leverage outliers make linear models sensitive without logarithmic scaling.
   - Tree-based models (such as **XGBoost**) naturally handle non-linear monotonic shifts and outliers effectively.
   - Engineering `TotalIncome`, `Debt_to_Income`, and `Loan_to_Income` normalizes debt capacity relative to scale.
"""))

# ── Cell 14: Correlation Heatmap Markdown ────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""## 5. Correlation Heatmap of Numeric Features

Measuring linear associations among numeric variables and the binary target `Loan_Status` ($Y=1, N=0$).
"""))

# ── Cell 15: Correlation Heatmap Code ────────────────────────────────────────
cells.append(nbf.v4.new_code_cell("""# Prepare numeric dataframe for correlation
corr_df = df_clean[[
    "ApplicantIncome", "CoapplicantIncome", "TotalIncome",
    "LoanAmount", "Loan_Amount_Term", "Credit_History"
]].copy()

# Add binary encoded target
corr_df["Loan_Status_Approved"] = (df_clean["Loan_Status"] == "Y").astype(int)

# Compute correlation matrix
corr_matrix = corr_df.corr()

plt.figure(figsize=(10, 7))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
cmap = sns.diverging_palette(230, 20, as_cmap=True)

sns.heatmap(
    corr_matrix,
    mask=mask,
    annot=True,
    fmt=".3f",
    cmap="coolwarm",
    vmin=-0.2,
    vmax=0.8,
    linewidths=0.5,
    cbar_kws={"shrink": 0.8}
)
plt.title("Correlation Matrix of Numeric Features & Target", pad=15)
plt.tight_layout()
plt.show()

# Display direct correlations with target
target_corr = corr_matrix["Loan_Status_Approved"].sort_values(ascending=False).to_frame(name="Correlation with Loan_Status (Approved)")
display(target_corr)
"""))

# ── Cell 16: Correlation Markdown Findings ───────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""### 💡 Finding 4: Correlation Highlights
1. **Target Correlation**:
   - `Credit_History` has an overwhelming correlation of **+0.541** with loan approval. No other raw numeric feature has a correlation exceeding $\\pm 0.10$.
2. **Feature Collinearity**:
   - `LoanAmount` is strongly positively correlated with `TotalIncome` (**+0.620**) and `ApplicantIncome` (**+0.566**). Higher earners predictably request larger credit lines.
   - `Loan_Amount_Term` has negligible direct correlation with approval ($-0.021$).
"""))

# ── Cell 17: Synthesis Markdown ──────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""## 6. Synthesis & Pipeline Recommendations

Based on this exploratory analysis, our machine learning pipeline in `02_model_training.ipynb` adheres to the following principles:

| EDA Finding | Machine Learning Decision |
|---|---|
| **Class imbalance (68.7% vs 31.3%)** | Apply **SMOTE** strictly on the training set to boost minority class recognition without test leakage. |
| **Credit_History dominates (~10× multiplier)** | Ensure `Credit_History` is cleanly imputed (median = 1.0) and verify via SHAP feature importance. |
| **Non-linear income & loan distributions** | Use **XGBoost Classifier**, which is invariant to monotonic transformations and handles skewed values gracefully. |
| **Multi-attribute income interaction** | Engineer domain features: `TotalIncome`, `Debt_to_Income` (EMI / Income), and `Loan_to_Income`. |
| **Categorical disparities (Area, Education, Marital)** | Employ **One-Hot Encoding** (`drop_first=True`) across all categories. |
"""))

nb.cells = cells

# Save unexecuted notebook
output_path = NOTEBOOKS_DIR / "01_eda.ipynb"
with open(output_path, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"Notebook created at: {output_path}")

# Execute via jupyter nbconvert
print("Executing notebook via nbconvert...")
res = subprocess.run([
    sys.executable, "-m", "jupyter", "nbconvert",
    "--to", "notebook",
    "--execute", str(output_path),
    "--output", "01_eda.ipynb",
    "--ExecutePreprocessor.timeout=180"
], capture_output=True, text=True)

if res.returncode == 0:
    print("[OK] Notebook successfully executed and rendered!")
else:
    print("Execution output:")
    print(res.stdout)
    print("Execution error:")
    print(res.stderr)
