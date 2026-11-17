# CrediPredict AI — Loan Approval Prediction

An academic Flask application using a Decision Tree trained on 10,000 synthetic loan records. Saved holdout accuracy: 87.65%.

## Folder structure

```text
ai application/
├── app.py                     # Small launcher; imports the backend
├── start_app.bat               # Windows one-click launcher
├── requirements.txt           # Python dependencies
├── frontend/
│   ├── templates/
│   │   ├── dashboard.html     # Current frontend page shown at /
│   │   └── index.html         # Previous UI, retained for reference
│   └── static/
│       ├── css/               # Page styling
│       ├── js/                # Browser interaction and API requests
│       ├── img/               # Image assets
│       └── Loan_Approval_Prediction_Project_Report.md # Downloadable report copy
├── backend/
│   ├── __init__.py
│   └── app.py                 # Flask routes, validation, prediction, JSON responses
├── ml/
│   ├── __init__.py
│   ├── train_model.py         # Synthetic data generation, preparation, training, evaluation
│   ├── export_pkl.py          # Export existing model to pickle files
│   └── demo_pkl.py            # Load and verify pickle files for demonstration
├── data/
│   └── loan_prediction_dataset.csv
├── models/
│   ├── loan_decision_tree_model.joblib # Bundle used by the backend
│   ├── loan_decision_tree_model.pkl   # Trained classifier alone
│   ├── preprocessing.pkl             # Category mappings and feature order
│   ├── loan_model_bundle.pkl         # Classifier and mappings together
│   └── model_metrics.json            # Saved evaluation results
├── tests/
│   ├── __init__.py
│   └── test_model.py           # Model, API, and validation checks
├── docs/
│   ├── EXPLAIN_PROJECT.md     # File-by-file explanation and viva walkthrough
│   ├── Loan_Approval_Prediction_Project_Report.md
│   ├── presentations/        # PowerPoint and PDF presentations
│   └── screenshots/          # Existing UI previews
└── output/                    # Local server logs
```

`.ppt-build/` and `__pycache__/` are generated working folders, not application source.

## Run

Double-click `start_app.bat`, or run these commands from the project folder:

```powershell
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000/ . The HTML uses Flask templates, so view it through the server.

## Demonstrate and maintain the model

```powershell
python -m ml.demo_pkl
python -m ml.export_pkl
python -m unittest discover -s tests -v
```

Optional retraining (regenerates the synthetic dataset and replaces model artifacts):

```powershell
python -m ml.train_model
```

Training updates both joblib and pickle exports. The three pickle files are exports of the same model, not three separately trained models. `preprocessing.pkl` holds metadata; feature calculations are implemented in Python. Only load trusted pickle files with a compatible Python/scikit-learn environment.

See [the explanation guide](docs/EXPLAIN_PROJECT.md) for a demonstration order.

## End semester presentation
Start with [START_HERE.md](START_HERE.md). The `presentation/` folder contains the selected final PPT, PDF and editable report. Open `CrediPredict.code-workspace` for an uncluttered editor view. Run `python scripts/demo_check.py` for a read-only preflight, then `start_app.bat` for the live server. Keep its terminal open throughout the demo.
