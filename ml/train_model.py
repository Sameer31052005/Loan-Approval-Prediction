import os
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib
from ml.export_pkl import export_pickle_artifacts

ROOT = Path(__file__).resolve().parents[1]

def create_or_load_dataset(filepath=ROOT / "data/loan_prediction_dataset.csv", n=10000, force_regenerate=True):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if os.path.exists(filepath) and not force_regenerate:
        print(f"Loading existing dataset from {filepath}...")
        df = pd.read_csv(filepath)
        if len(df) == n:
            return df

    print(f"Generating Kaggle-aligned Loan Prediction dataset ({n:,} records)...")
    np.random.seed(42)

    loan_ids = [f"LP{str(i).zfill(6)}" for i in range(1001, 1001 + n)]
    genders = np.random.choice(["Male", "Female"], size=n, p=[0.81, 0.19])
    married = np.random.choice(["Yes", "No"], size=n, p=[0.65, 0.35])
    dependents = np.random.choice(["0", "1", "2", "3+"], size=n, p=[0.58, 0.17, 0.17, 0.08])
    education = np.random.choice(["Graduate", "Not Graduate"], size=n, p=[0.78, 0.22])
    self_employed = np.random.choice(["No", "Yes"], size=n, p=[0.86, 0.14])

    # Income distributions typical of Kaggle dataset
    applicant_income = np.random.lognormal(mean=8.4, sigma=0.55, size=n).astype(int)
    applicant_income = np.clip(applicant_income, 1200, 45000)

    # Coapplicant income (approx 55% have co-borrower)
    has_coapplicant = np.random.choice([0, 1], size=n, p=[0.45, 0.55])
    coapplicant_income = (has_coapplicant * np.random.lognormal(mean=7.4, sigma=0.75, size=n)).astype(int)
    coapplicant_income = np.clip(coapplicant_income, 0, 25000)

    # Loan Amount in thousands (typically 35k to 650k)
    total_income = applicant_income + coapplicant_income
    loan_amount = (total_income * np.random.uniform(0.016, 0.032) + np.random.normal(30, 18, size=n)).astype(int)
    loan_amount = np.clip(loan_amount, 30, 680)

    # Loan terms in months (360 is dominant: ~83%)
    terms = np.random.choice([120, 180, 240, 300, 360, 480], size=n, p=[0.02, 0.08, 0.03, 0.02, 0.83, 0.02])

    # Credit History is the primary predictor in the Kaggle dataset (~84% have 1.0)
    credit_history = np.random.choice([1.0, 0.0], size=n, p=[0.84, 0.16])

    property_area = np.random.choice(["Urban", "Semiurban", "Rural"], size=n, p=[0.33, 0.38, 0.29])

    # Target loan approval probability calculation reflecting Kaggle ground truth:
    loan_status = []
    for i in range(n):
        ch = credit_history[i]
        inc = total_income[i]
        amt = loan_amount[i]
        edu = 1 if education[i] == "Graduate" else 0
        prop = 1.08 if property_area[i] == "Semiurban" else (1.0 if property_area[i] == "Urban" else 0.92)

        if ch == 0.0:
            # High default risk - only very high income with small loans rarely approved
            prob_approve = 0.07 if (inc > 12000 and amt < 130) else 0.03
        else:
            # Good credit history
            affordability_ratio = (amt * 1000) / (inc * 12 + 1)
            base_prob = 0.88 * prop
            if affordability_ratio > 3.0:
                base_prob -= 0.22
            if edu == 0:
                base_prob -= 0.04
            prob_approve = np.clip(base_prob, 0.58, 0.96)

        status = "Y" if np.random.rand() < prob_approve else "N"
        loan_status.append(status)

    df = pd.DataFrame({
        "Loan_ID": loan_ids,
        "Gender": genders,
        "Married": married,
        "Dependents": dependents,
        "Education": education,
        "Self_Employed": self_employed,
        "ApplicantIncome": applicant_income,
        "CoapplicantIncome": coapplicant_income,
        "LoanAmount": loan_amount,
        "Loan_Amount_Term": terms,
        "Credit_History": credit_history,
        "Property_Area": property_area,
        "Loan_Status": loan_status
    })

    df.to_csv(filepath, index=False)
    print(f"Dataset successfully saved with {len(df):,} records to {filepath}")
    return df

def preprocess_and_train():
    df = create_or_load_dataset(n=10000, force_regenerate=True)
    print("Dataset distribution:")
    print(df["Loan_Status"].value_counts(normalize=True))

    # Feature Engineering
    df_proc = df.copy()
    df_proc["Total_Income"] = df_proc["ApplicantIncome"] + df_proc["CoapplicantIncome"]
    df_proc["Income_to_Loan_Ratio"] = df_proc["Total_Income"] / (df_proc["LoanAmount"] + 1e-5)
    df_proc["EMI_Estimate"] = (df_proc["LoanAmount"] * 1000) / (df_proc["Loan_Amount_Term"] + 1e-5)

    # Encode categorical features
    cat_mappings = {
        "Gender": {"Male": 1, "Female": 0},
        "Married": {"Yes": 1, "No": 0},
        "Dependents": {"0": 0, "1": 1, "2": 2, "3+": 3},
        "Education": {"Graduate": 1, "Not Graduate": 0},
        "Self_Employed": {"Yes": 1, "No": 0},
        "Property_Area": {"Rural": 0, "Semiurban": 1, "Urban": 2},
        "Loan_Status": {"Y": 1, "N": 0}
    }

    feature_cols = [
        "ApplicantIncome",
        "CoapplicantIncome",
        "Total_Income",
        "LoanAmount",
        "Loan_Amount_Term",
        "Credit_History",
        "Gender",
        "Married",
        "Dependents",
        "Education",
        "Self_Employed",
        "Property_Area",
        "Income_to_Loan_Ratio",
        "EMI_Estimate"
    ]

    for col, mapping in cat_mappings.items():
        if col in df_proc.columns:
            df_proc[col] = df_proc[col].map(mapping).fillna(0).astype(int)

    X = df_proc[feature_cols]
    y = df_proc["Loan_Status"]

    # 80:20 Train-Test Split (8,000 Train / 2,000 Test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # Train Decision Tree Classifier with max_depth=4 for interpretability
    clf = DecisionTreeClassifier(
        criterion="gini",
        max_depth=4,
        min_samples_split=20,
        min_samples_leaf=10,
        random_state=42
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    y_pred_proba = clf.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred).tolist()

    print("\n================ MODEL PERFORMANCE (10,000 RECORDS) ================")
    print(f"Accuracy:  {acc * 100:.2f}%")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"Confusion Matrix (2,000 Test Cases): {cm}")

    # Feature Importance
    importances = dict(zip(feature_cols, clf.feature_importances_))
    sorted_importances = sorted(importances.items(), key=lambda x: x[1], reverse=True)
    print("\nFeature Importances:")
    for feat, imp in sorted_importances:
        if imp > 0.001:
            print(f"  - {feat}: {imp * 100:.2f}%")

    # Tree textual rules
    tree_rules = export_text(clf, feature_names=feature_cols)

    # Save model artifacts
    os.makedirs(ROOT / "models", exist_ok=True)
    model_payload = {
        "model": clf,
        "feature_cols": feature_cols,
        "cat_mappings": cat_mappings
    }
    joblib.dump(model_payload, ROOT / "models/loan_decision_tree_model.joblib")
    export_pickle_artifacts(model_payload, ROOT / "models")

    metrics_payload = {
        "model_name": "Decision Tree Classifier",
        "criterion": "gini",
        "max_depth": 4,
        "accuracy": round(float(acc) * 100, 2),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1_score": round(float(f1), 4),
        "confusion_matrix": {
            "true_negative": cm[0][0],
            "false_positive": cm[0][1],
            "false_negative": cm[1][0],
            "true_positive": cm[1][1]
        },
        "feature_importances": [
            {"feature": f, "importance": round(float(imp) * 100, 2)}
            for f, imp in sorted_importances if imp > 0.001
        ],
        "dataset_size": len(df),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "tree_rules_snippet": tree_rules[:1400]
    }

    with open(ROOT / "models/model_metrics.json", "w") as f:
        json.dump(metrics_payload, f, indent=2)

    print("\nModel saved to models/loan_decision_tree_model.joblib")
    print("Metrics saved to models/model_metrics.json")
    return metrics_payload

if __name__ == "__main__":
    preprocess_and_train()
