import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('cli/.env')

response = requests.post(
    'http://localhost:8000/api/aws/fetch',
    json={
        'access_key': os.getenv('AWS_ACCESS_KEY_ID'),
        'secret_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'region': 'us-east-1',
        'bucket_name': 'carboniq-bucket',
        'file_key': 'carboniq-cur/carboniq-cur/data/BILLING_PERIOD=2026-10/carboniq-cur-00001.csv.zip'
    },
    timeout=300
)

data = response.json()
print(json.dumps(data, indent=2))
