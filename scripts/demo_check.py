"""Read-only preflight and three demo scenarios. Never retrains the model."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
for name in ['models/loan_decision_tree_model.joblib','models/model_metrics.json','data/loan_prediction_dataset.csv','frontend/templates/dashboard.html']:
    if not (ROOT/name).is_file():
        raise SystemExit(f'Missing required file: {name}')
from backend.app import app
client=app.test_client()
assert client.get('/').status_code == 200
assert client.get('/api/metrics').status_code == 200
base=client.get('/api/samples').get_json()['samples'][0]['data']
base.update(ApplicantIncome=75000, CoapplicantIncome=31995, LoanAmount=150, Loan_Amount_Term=12, Credit_History=1)
for name,changes,expected in [('Positive credit',{},1),('Negative credit',{'Credit_History':0},0),('Affordability guard',{'LoanAmount':10000},0)]:
    response=client.post('/api/predict',json=dict(base,**changes))
    assert response.status_code==200, response.get_json()
    result=response.get_json()
    assert result['decision']==expected, result
    print(f"PASS: {name}: {result['status']}, approval {result['approval_probability']}%")
print('Preflight passed. Saved model loaded; no training performed.')
