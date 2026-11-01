# Credit Risk Assessment and Loan Approval (LoanIQ)

> **An End-to-End AI-Powered Credit Scoring, Risk Band Categorization & Loan Approval System with Explainable AI (SHAP).**

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![XGBoost](https://img.shields.io/badge/XGBoost-Tuned-EB5424?logo=xgboost&logoColor=white)](https://xgboost.readthedocs.io)
[![SHAP](https://img.shields.io/badge/XAI-SHAP-06B6D4)](https://shap.readthedocs.io)

---

## 📌 Project Overview

**LoanIQ** is a full-stack data science and machine learning web application designed to evaluate loan applicants in real time, predict default risk, and categorize credit risk into actionable tiers (**Low**, **Medium**, **High**).

Unlike traditional "black-box" credit scoring algorithms, LoanIQ integrates **SHAP (Shapley Additive exPlanations)** to provide transparent, game-theoretic explanations showing the exact positive and negative financial factors that influenced each individual credit decision.

---

## 🎯 Key Features

- **Instant Credit Scoring & Approval**: Predicts loan status (`Approved` vs. `Rejected`) along with a confidence percentage.
- **3-Tier Risk Band Categorization**: Segregates applicants into Low Risk ($\ge 70\%$), Medium Risk ($45\%-70\%$), and High Risk ($< 45\%$).
- **Explainable AI (XAI with SHAP)**:
  - Highlights the **Top 3 Decision Drivers** (e.g., Credit History boost vs. High Debt penalty).
  - Visualizes a full feature attribution bar chart for transparency and compliance.
- **Role-Based Portals**:
  - **Applicant Portal**: Clean submission form with instant AI verdict and explainability breakdown.
  - **Officer / Admin Dashboard**: Real-time analytics, portfolio KPIs, interactive Recharts visualizations (approval by location, education, and monthly trends), and application audit table with search, filter, and drilldown modals.
- **Production-Ready ML Pipeline**:
  - Addresses class imbalance with **SMOTE** (Synthetic Minority Over-sampling Technique).
  - Feature engineering: Computes **Debt-to-Income (DTI)** and **Loan-to-Income (LTI)** ratios.
  - Champion model: **XGBoost Classifier** fine-tuned with **GridSearchCV** (**82.93% Accuracy**, **88.24% Recall**).

---

## 🏗️ Project Architecture

```
Credit-Risk-Assessment-and-Loan-Approval/
├── backend/                          # Flask REST API
│   ├── app.py                        # App factory, CORS, blueprints & demo seeding
│   ├── database.py                   # SQLAlchemy instance
│   ├── routes/
│   │   ├── auth.py                   # POST /api/login, /api/register
│   │   ├── predict.py                # POST /api/predict (Inference & SHAP)
│   │   └── applications.py           # GET/DELETE /api/applications, /api/analytics
│   ├── utils/
│   │   └── shap_explain.py           # SHAP TreeExplainer wrapper
│   ├── models/
│   │   ├── model.pkl                 # Trained XGBoost model artifact
│   │   ├── feature_columns.json      # 17-feature input schema
│   │   └── background_data.csv       # Baseline sample for SHAP
│   └── requirements.txt              # Backend dependencies
│
├── frontend/                         # React 18 + Vite SPA
│   ├── src/
│   │   ├── pages/                    # Login, UserDashboard, AdminDashboard
│   │   ├── components/               # LoanForm, ResultCard, ApplicationsTable, AnalyticsCharts
│   │   └── api/api.js                # Axios client with JWT/Bearer interceptors
│   ├── vite.config.js                # Vite build configuration
│   └── package.json
│
├── data/
│   └── loan_data.csv                 # Kaggle loan prediction dataset
│
├── notebooks/
│   ├── 01_eda.ipynb                  # Exploratory Data Analysis
│   └── 02_model_training.ipynb       # 4-model benchmarking, SMOTE & hyperparameter tuning
│
├── scripts/
│   ├── build_and_run_eda.py          # Script generating 01_eda.ipynb
│   ├── build_and_run_notebook.py     # Script running training pipeline
│   └── generate_ppt.py               # Script generating PowerPoint presentation
│
├── Loan_Risk_Analysis_Presentation.pptx # 6-slide College Presentation Deck
├── package.json                      # Root scripts (launches both servers)
└── README.md
```

---

## 📊 Model Performance Comparison

Trained on 80% stratified split with SMOTE class balancing; evaluated on the 20% holdout test set:

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
|---|:---:|:---:|:---:|:---:|:---:|
| Logistic Regression | 81.30% | 89.74% | 82.35% | 85.89% | 0.8839 |
| Decision Tree | 79.67% | 84.09% | 87.06% | 85.55% | 0.8433 |
| Random Forest | 86.99% | 88.76% | 92.94% | 90.80% | 0.8842 |
| XGBoost (Default) | 82.11% | 86.21% | 88.24% | 87.21% | 0.8492 |
| **XGBoost (Fine-Tuned)** | **82.93%** | **87.21%** | **88.24%** | **87.72%** | **0.8418** |

---

## 🚀 Quick Start

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)

### 1. Clone the Repository
```bash
git clone https://github.com/kishansenghani/Credit-Risk-Assessment-and-Loan-Approval.git
cd Credit-Risk-Assessment-and-Loan-Approval
```

### 2. Install Dependencies
```bash
# Install frontend & root runner dependencies
npm install

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

### 3. Run the Application
```bash
npm run dev
```

This launches both servers concurrently:
- 🔵 **Backend (Flask API)**: `http://localhost:5000` *(auto-seeds demo users on first run)*
- 🟢 **Frontend (React + Vite)**: `http://localhost:5173`

---

## 🔑 Demo Credentials

| Role | Username | Password | Access |
|---|---|---|---|
| **Borrower / User** | `user` | `user123` | Loan Application Form, AI Credit Decision & SHAP Breakdown |
| **Admin / Loan Officer** | `admin` | `admin123` | Executive Analytics Dashboard, Interactive Charts & Applications Table |

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/login` | Authenticate user & retrieve session token |
| `POST` | `/api/register` | Create a new user account |
| `POST` | `/api/predict` | Preprocess features, run XGBoost prediction & compute SHAP values |
| `GET` | `/api/applications` | Paginated applications list with search & filter options |
| `GET` | `/api/applications/<id>` | Full application details & SHAP attributions |
| `DELETE` | `/api/applications/<id>` | Remove an application record |
| `GET` | `/api/analytics` | Portfolio KPIs, demographic distributions & monthly trends |

---

## 🛠️ Technology Stack

| Layer | Tools & Frameworks |
|---|---|
| **Frontend** | React 18, Vite, Recharts, Axios, Vanilla CSS3 |
| **Backend** | Python 3.13, Flask 3, Flask-SQLAlchemy, Flask-CORS |
| **Database** | SQLite (via SQLAlchemy ORM) |
| **Machine Learning** | XGBoost, Scikit-Learn, Imbalanced-Learn (SMOTE), SHAP, Joblib |
| **Data Processing** | Pandas, NumPy |

---

## 🎓 Academic Presentation
A complete 6-slide presentation deck is included in the root directory:
- 📁 **Presentation File**: `Loan_Risk_Analysis_Presentation.pptx`
- Covers: Title & Student Details, Project Overview & Problem Statement, User/Admin Workflows, System Architecture & Tech Stack, Future Scope, and Q&A.

---

## 👤 Author
**Kishan Senghani**  
- GitHub: [@kishansenghani](https://github.com/kishansenghani)
