# START HERE - End semester presentation

Group 6 | Section 117-B | Faculty: Subodh Bansal

## Open in Antigravity
Open this project folder, or open CrediPredict.code-workspace if your editor supports workspace files. The workspace hides generated build folders and old output versions. Source folders remain in their working locations.

## Final files
- presentation/01_Group6_Presentation.pptx - latest deck with output screenshots
- presentation/02_Group6_Report.pdf - report without the leftover template header
- presentation/03_Group6_Report.docx - editable copy

## Start the live demo
1. Open a terminal in this project folder.
2. Run .\start_app.bat (or double-click start_app.bat).
3. Wait for Running on http://127.0.0.1:5000 and open that address.
4. KEEP THE TERMINAL OPEN. Closing it stops the website.
5. Stop the server after presenting using Ctrl+C.

If dependencies are missing, install before class: python -m pip install -r requirements.txt
If port 5000 is busy, in PowerShell run $env:PORT='5001'; python app.py and open http://127.0.0.1:5001.
Do not open dashboard.html directly; it needs Flask.

## Teacher walkthrough in order
1. presentation/01_Group6_Presentation.pptx - explain problem and architecture.
2. data/loan_prediction_dataset.csv - 10,000 synthetic labeled records.
3. ml/train_model.py - feature engineering, 80:20 split, depth-4 tree.
4. models/model_metrics.json - saved metrics and confusion matrix.
5. backend/app.py - validation, prediction and affordability rule.
6. frontend/templates/dashboard.html - form and results layout.
7. frontend/static/js/dashboard.js - JSON request and INR conversion.
8. Live browser demo, then tests/test_model.py for validation.

## Three live examples
Use Male, Married Yes, Dependents 1, Graduate, Self Employed No, Semiurban.
- Income 75000, coapplicant 31995, full loan INR 150000, term 1 year, positive credit: approved.
- Change only credit history to negative and submit again: declined.
- Restore positive credit and use full loan INR 10000000, 1 year: affordability rejection.
Always click Analyze again after editing inputs. Probabilities depend on the complete profile.

## Key viva answers
- Model: Decision Tree, Gini, maximum depth 4.
- Training/testing: 8000 / 2000, stratified, random seed 42.
- Accuracy 87.65%, precision 85.95%, recall 99.24%, F1 92.12%.
- TP 1444, TN 309, FP 236, FN 11. Positive means approved.
- Data is locally generated synthetic data, not an actual Kaggle download.
- Monthly EMI display is principal divided by months; interest is excluded.
- Full form takes INR; JavaScript divides the loan amount by 1000 for the model.
- The 40% affordability rule is separate from the tree. Saved metrics describe the tree.
- Rejection recall is 56.70%; high approval recall does not mean perfect predictions.
- Pickle/joblib files save the trained model. They are not separate algorithms.

## Before leaving for class
Run python scripts/demo_check.py and python -m unittest discover -s tests -v.
Open the final PPT and PDF once. Keep a backup copy on a USB drive.
Do not retrain during the presentation: python -m ml.train_model replaces data and model artifacts.
If the live demo fails, the PPT contains actual output screenshots for explanation.
