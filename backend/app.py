import os
from pathlib import Path
import json
import math
import joblib
import pandas as pd
from flask import Flask, render_template, request, jsonify

ROOT = Path(__file__).resolve().parents[1]
app = Flask(__name__, static_folder=str(ROOT / "frontend/static"),
            template_folder=str(ROOT / "frontend/templates"), static_url_path="/static")

# Paths
MODEL_PATH = ROOT / "models/loan_decision_tree_model.joblib"
METRICS_PATH = ROOT / "models/model_metrics.json"

# Global model cache
model_bundle = None
model_metrics = None

def get_model_bundle():
    global model_bundle
    if model_bundle is None:
        if os.path.exists(MODEL_PATH):
            model_bundle = joblib.load(MODEL_PATH)
        else:
            # If not yet trained, trigger training
            from ml.train_model import preprocess_and_train
            preprocess_and_train()
            model_bundle = joblib.load(MODEL_PATH)
    return model_bundle

def get_metrics():
    global model_metrics
    if os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, "r") as f:
            model_metrics = json.load(f)
    return model_metrics

@app.route("/")
def index():
    metrics = get_metrics()
    return render_template("dashboard.html", metrics=metrics)

@app.route("/api/metrics", methods=["GET"])
def api_metrics():
    metrics = get_metrics()
    return jsonify(metrics)

@app.route("/api/samples", methods=["GET"])
def api_samples():
    samples = [
        {
            "id": "prime",
            "name": "Prime Borrower (High Income & Clean Credit)",
            "tag": "High Approval Likelihood",
            "tagColor": "green",
            "data": {
                "Gender": "Male",
                "Married": "Yes",
                "Dependents": "1",
                "Education": "Graduate",
                "Self_Employed": "No",
                "ApplicantIncome": 7500,
                "CoapplicantIncome": 3200,
                "LoanAmount": 150,
                "Loan_Amount_Term": 180,
                "Credit_History": 1,
                "Property_Area": "Semiurban"
            }
        },
        {
            "id": "defaulter",
            "name": "Defaulter Risk (Negative Credit Record)",
            "tag": "Immediate High Risk",
            "tagColor": "red",
            "data": {
                "Gender": "Male",
                "Married": "No",
                "Dependents": "0",
                "Education": "Not Graduate",
                "Self_Employed": "No",
                "ApplicantIncome": 3200,
                "CoapplicantIncome": 0,
                "LoanAmount": 180,
                "Loan_Amount_Term": 180,
                "Credit_History": 0,
                "Property_Area": "Rural"
            }
        },
        {
            "id": "borderline",
            "name": "Borderline / High Debt-to-Income",
            "tag": "Tight Affordability",
            "tagColor": "amber",
            "data": {
                "Gender": "Female",
                "Married": "Yes",
                "Dependents": "2",
                "Education": "Graduate",
                "Self_Employed": "Yes",
                "ApplicantIncome": 3800,
                "CoapplicantIncome": 1200,
                "LoanAmount": 260,
                "Loan_Amount_Term": 180,
                "Credit_History": 1,
                "Property_Area": "Urban"
            }
        }
    ]
    return jsonify({"samples": samples})

@app.route("/api/predict", methods=["POST"])
def api_predict():
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Send a JSON object with applicant details."}), 400
        bundle = get_model_bundle()
        model = bundle["model"]
        feature_cols = bundle["feature_cols"]
        cat_mappings = bundle["cat_mappings"]

        # Parse & Validate numeric inputs
        applicant_inc = float(data.get("ApplicantIncome", 0))
        coapplicant_inc = float(data.get("CoapplicantIncome", 0))
        loan_amount = float(data.get("LoanAmount", 0))
        loan_term = float(data.get("Loan_Amount_Term", 180))
        credit_history = float(data.get("Credit_History", 1))
        if not all(math.isfinite(v) for v in [applicant_inc, coapplicant_inc, loan_amount, loan_term, credit_history]):
            return jsonify({"error": "Numeric inputs must be finite."}), 400
        if applicant_inc < 0 or coapplicant_inc < 0:
            return jsonify({"error": "Income cannot be negative."}), 400
        if credit_history not in (0, 1):
            return jsonify({"error": "Credit history must be 0 or 1."}), 400
        for key, mapping in cat_mappings.items():
            if key != "Loan_Status" and key in data and str(data[key]) not in mapping:
                return jsonify({"error": f"Invalid {key}."}), 400

        if loan_amount <= 0:
            return jsonify({"error": "Loan amount must be greater than zero."}), 400
        if (applicant_inc + coapplicant_inc) <= 0:
            return jsonify({"error": "Total household income must be greater than zero."}), 400
        if loan_term <= 0:
            return jsonify({"error": "Loan term must be positive."}), 400

        # Derived metrics
        total_income = applicant_inc + coapplicant_inc
        income_to_loan = total_income / (loan_amount + 1e-5)
        emi_estimate = (loan_amount * 1000) / (loan_term + 1e-5)
        dti_ratio = round((emi_estimate / (total_income + 1e-5)) * 100, 2)

        # Categoricals
        gender_val = cat_mappings["Gender"].get(data.get("Gender", "Male"), 1)
        married_val = cat_mappings["Married"].get(data.get("Married", "Yes"), 1)
        dependents_val = cat_mappings["Dependents"].get(str(data.get("Dependents", "0")), 0)
        education_val = cat_mappings["Education"].get(data.get("Education", "Graduate"), 1)
        self_employed_val = cat_mappings["Self_Employed"].get(data.get("Self_Employed", "No"), 0)
        prop_area_val = cat_mappings["Property_Area"].get(data.get("Property_Area", "Semiurban"), 1)

        input_row = {
            "ApplicantIncome": applicant_inc,
            "CoapplicantIncome": coapplicant_inc,
            "Total_Income": total_income,
            "LoanAmount": loan_amount,
            "Loan_Amount_Term": loan_term,
            "Credit_History": credit_history,
            "Gender": gender_val,
            "Married": married_val,
            "Dependents": dependents_val,
            "Education": education_val,
            "Self_Employed": self_employed_val,
            "Property_Area": prop_area_val,
            "Income_to_Loan_Ratio": income_to_loan,
            "EMI_Estimate": emi_estimate
        }

        X_input = pd.DataFrame([input_row])[feature_cols]

        # Model Inference via Decision Tree
        pred_class = int(model.predict(X_input)[0])
        pred_proba = model.predict_proba(X_input)[0]
        approval_prob = round(float(pred_proba[1]) * 100, 2)
        rejection_prob = round(float(pred_proba[0]) * 100, 2)

        # Do not allow the model to approve loans whose principal alone is
        # unaffordable. This guard also handles very large INR amounts that
        # are outside the synthetic training data range.
        affordability_limit_pct = 40.0
        affordability_passed = dti_ratio <= affordability_limit_pct
        if not affordability_passed:
            pred_class = 0
            approval_prob = 0.0
            rejection_prob = 100.0

        status = "Approved" if pred_class == 1 else "Rejected"
        path = []
        for node in model.decision_path(X_input).indices:
            feature_index = model.tree_.feature[node]
            if feature_index < 0:
                continue
            feature = feature_cols[feature_index]
            value = float(X_input.iloc[0, feature_index])
            threshold = float(model.tree_.threshold[node])
            operator = "<=" if value <= threshold else ">"
            path.append({"feature": feature, "value": value, "threshold": threshold, "operator": operator})

        # Automated Risk Assessment Categorization
        if credit_history == 0.0:
            risk_tier = "High Default Risk"
            risk_color = "#ef4444" # red
        elif approval_prob >= 75:
            risk_tier = "Low Credit Risk"
            risk_color = "#10b981" # green
        elif approval_prob >= 50:
            risk_tier = "Moderate Risk (Manual Review Advised)"
            risk_color = "#f59e0b" # amber
        else:
            risk_tier = "Substantial Risk"
            risk_color = "#ef4444" # red

        # Rule-based decision factors from Decision Tree splits
        reasons = []
        if credit_history == 1.0:
            reasons.append("Credit History Guidelines: Satisfactory credit track record met.")
        else:
            reasons.append("Credit History Flag: Prior default or missing credit history detected.")

        if total_income >= 6000:
            reasons.append(f"Income Capacity: Combined monthly income of INR {total_income:,.0f} satisfies prime debt servicing.")
        elif total_income < 3500:
            reasons.append(f"Income Alert: Combined monthly income of INR {total_income:,.0f} is in the lower quintile.")

        if dti_ratio > 40:
            reasons.append(f"High Debt Burden: Estimated monthly EMI represents ~{dti_ratio}% of total income.")
        else:
            reasons.append(f"Healthy Debt Burden: Estimated monthly EMI represents ~{dti_ratio}% of total income.")

        if not affordability_passed:
            reasons.append(f"Affordability Rule: Estimated principal is {dti_ratio}% of income, above the {affordability_limit_pct:.0f}% limit.")

        if data.get("Education") == "Graduate":
            reasons.append("Education Factor: Graduate qualification contributes positively to income stability.")

        return jsonify({
            "status": status,
            "decision_path": path,
            "leaf_id": int(model.apply(X_input)[0]),
            "decision": 1 if status == "Approved" else 0,
            "approval_probability": approval_prob,
            "rejection_probability": rejection_prob,
            "risk_tier": risk_tier,
            "risk_color": risk_color,
            "derived_metrics": {
                "total_income": total_income,
                "loan_amount_k": loan_amount,
                "estimated_monthly_emi": round(emi_estimate, 2),
                "debt_to_income_pct": dti_ratio,
                "term_months": int(loan_term)
            },
            "decision_factors": [f"{p['feature']} ({p['value']:.2f}) {p['operator']} {p['threshold']:.2f}" for p in path] + ([f"Affordability guard: debt-to-income {dti_ratio}% > {affordability_limit_pct:.0f}%"] if not affordability_passed else [])
        })

    except (ValueError, TypeError):
        return jsonify({"error": "Please enter valid numeric values."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Loan Approval Prediction Server on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
