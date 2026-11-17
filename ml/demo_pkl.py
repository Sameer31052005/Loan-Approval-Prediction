"""Load the pickle artifacts and verify predictions against the original model."""
import pickle
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


def main():
    root = Path(__file__).resolve().parents[1]
    models = root / "models"
    with (models / "loan_model_bundle.pkl").open("rb") as handle:
        bundle = pickle.load(handle)
    with (models / "loan_decision_tree_model.pkl").open("rb") as handle:
        model = pickle.load(handle)
    with (models / "preprocessing.pkl").open("rb") as handle:
        preprocessing = pickle.load(handle)
    original = joblib.load(models / "loan_decision_tree_model.joblib")
    assert preprocessing["feature_cols"] == original["feature_cols"]
    assert preprocessing["cat_mappings"] == original["cat_mappings"]
    df = pd.read_csv(root / "data/loan_prediction_dataset.csv")
    df["Total_Income"] = df.ApplicantIncome + df.CoapplicantIncome
    df["Income_to_Loan_Ratio"] = df.Total_Income / (df.LoanAmount + 1e-5)
    df["EMI_Estimate"] = df.LoanAmount * 1000 / (df.Loan_Amount_Term + 1e-5)
    for column, mapping in preprocessing["cat_mappings"].items():
        df[column] = df[column].map(mapping).fillna(0).astype(int)
    features = df[preprocessing["feature_cols"]]
    for candidate in (model, bundle["model"]):
        np.testing.assert_array_equal(candidate.predict(features), original["model"].predict(features))
        np.testing.assert_allclose(candidate.predict_proba(features), original["model"].predict_proba(features))
    print(f"Loaded: {type(model).__name__}, depth={model.get_depth()}")
    print(f"Input features: {len(preprocessing['feature_cols'])}")
    print(f"Verified: predictions and probabilities match the original on all {len(df):,} rows.")
    prediction = model.predict(features.iloc[[0]])[0]
    print(f"First dataset row model prediction: {'Approved' if prediction == 1 else 'Rejected'}")
    print("The web app additionally applies its affordability rule to the model output.")


if __name__ == "__main__":
    main()
