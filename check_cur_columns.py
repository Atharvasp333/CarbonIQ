import boto3
import zipfile
import io
import csv
import os
from dotenv import load_dotenv

load_dotenv('cli/.env')

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='us-east-1'
)

print("Downloading and checking CUR CSV columns...")
print("="*60)

# Download the file
response = s3.get_object(
    Bucket='carboniq-bucket',
    Key='carboniq-cur/carboniq-cur/data/BILLING_PERIOD=2026-10/carboniq-cur-00001.csv.zip'
)

# Extract ZIP
content_bytes = response['Body'].read()
with zipfile.ZipFile(io.BytesIO(content_bytes)) as zip_file:
    csv_file = [f for f in zip_file.namelist() if f.endswith('.csv')][0]
    csv_content = zip_file.read(csv_file).decode('utf-8')

# Check columns
lines = csv_content.split('\n')
headers = lines[0].split(',')

print(f"\nFound {len(headers)} columns:\n")
for i, col in enumerate(headers[:30], 1):  # Show first 30
    print(f"  {i}. {col}")

if len(headers) > 30:
    print(f"  ... and {len(headers) - 30} more columns")

print(f"\n{'='*60}")
print(f"Total rows in CSV: {len(lines) - 1}")
print(f"Sample row:\n{lines[1][:200]}...")
