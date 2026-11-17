"""Export the existing trained model as standard Python pickle artifacts."""
import pickle
from pathlib import Path

import joblib


def export_pickle_artifacts(bundle, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "loan_model_bundle.pkl": bundle,
        "loan_decision_tree_model.pkl": bundle["model"],
        "preprocessing.pkl": {
            "feature_cols": bundle["feature_cols"],
            "cat_mappings": bundle["cat_mappings"],
        },
    }
    for name, value in artifacts.items():
        with (output_dir / name).open("wb") as handle:
            pickle.dump(value, handle, protocol=pickle.HIGHEST_PROTOCOL)
        print(f"Saved {output_dir / name}")


if __name__ == "__main__":
    models_dir = Path(__file__).resolve().parents[1] / "models"
    export_pickle_artifacts(
        joblib.load(models_dir / "loan_decision_tree_model.joblib"), models_dir
    )
