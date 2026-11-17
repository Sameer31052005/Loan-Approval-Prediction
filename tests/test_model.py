import json
import unittest
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
from backend.app import app, get_model_bundle


ROOT = Path(__file__).resolve().parents[1]


class ModelChecks(unittest.TestCase):
    def test_saved_model_and_api(self):
        bundle = get_model_bundle()
        df = pd.read_csv(ROOT / 'data/loan_prediction_dataset.csv')
        df['Total_Income'] = df.ApplicantIncome + df.CoapplicantIncome
        df['Income_to_Loan_Ratio'] = df.Total_Income / (df.LoanAmount + 1e-5)
        df['EMI_Estimate'] = df.LoanAmount * 1000 / (df.Loan_Amount_Term + 1e-5)
        encoded = df.copy()
        for col, mapping in bundle['cat_mappings'].items():
            encoded[col] = encoded[col].map(mapping).fillna(0).astype(int)
        _, test = train_test_split(encoded, test_size=.2, random_state=42, stratify=encoded.Loan_Status)
        predictions = bundle['model'].predict(test[bundle['feature_cols']])
        metrics = json.loads((ROOT / 'models/model_metrics.json').read_text())
        self.assertEqual(round(accuracy_score(test.Loan_Status, predictions)*100, 2), metrics['accuracy'])
        self.assertEqual(confusion_matrix(test.Loan_Status, predictions).ravel().tolist(), [309, 236, 11, 1444])
        client = app.test_client()
        for index, expected in zip(test.index[:100], predictions[:100]):
            payload = df.loc[index].to_dict()
            response = client.post('/api/predict', json=payload)
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data['decision'], int(expected))
            self.assertAlmostEqual(data['approval_probability']+data['rejection_probability'], 100, places=2)
            row = encoded.loc[[index], bundle['feature_cols']]
            self.assertEqual(data['leaf_id'], int(bundle['model'].apply(row)[0]))
            self.assertEqual(len(data['decision_path']), len(bundle['model'].decision_path(row).indices)-1)
        print('Holdout: 2,000 rows; accuracy 87.65%; 100 API predictions match saved model.')

    def test_validation_and_samples(self):
        c = app.test_client()
        self.assertEqual(c.get('/').status_code, 200)
        samples = c.get('/api/samples').get_json()['samples']
        for sample in samples:
            result = c.post('/api/predict', json=sample['data'])
            self.assertEqual(result.status_code, 200)
            print(sample['id'], result.get_json()['status'], result.get_json()['approval_probability'])
        for key, value in [('ApplicantIncome', -1), ('LoanAmount', 0), ('Loan_Amount_Term', 0), ('Credit_History', 2), ('Education', 'invalid'), ('ApplicantIncome', 'NaN'), ('LoanAmount', None)]:
            payload = dict(samples[0]['data'], **{key:value})
            self.assertEqual(c.post('/api/predict', json=payload).status_code, 400, (key, value))
        self.assertEqual(c.post('/api/predict', json=[]).status_code, 400)


if __name__ == '__main__':
    unittest.main()
