"""
Test AWS S3 integration with your credentials
"""
import os
import requests
from dotenv import load_dotenv

# Load from cli/.env
load_dotenv("cli/.env")

# Get credentials
access_key = os.getenv("AWS_ACCESS_KEY_ID")
secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
region = os.getenv("AWS_REGION", "us-east-1")
bucket = os.getenv("AWS_BUCKET_NAME", "carboniq-bucket")
prefix = os.getenv("AWS_FILE_PREFIX", "carboniq-cur/carboniq-cur/data/")

print("🧪 Testing AWS S3 Integration")
print("="*60)
print(f"Bucket: {bucket}")
print(f"Region: {region}")
print(f"Prefix: {prefix}")
print(f"Access Key: {access_key[:8]}...")
print("="*60)

# Test 1: List files
print("\n📋 Test 1: List available CSV files...")
try:
    response = requests.post(
        "http://localhost:8000/api/aws/list-files",
        json={
            "access_key": access_key,
            "secret_key": secret_key,
            "region": region,
            "bucket_name": bucket,
            "prefix": prefix
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['count']} CSV files")
        
        if data['files']:
            print("\nAvailable files:")
            for i, file in enumerate(data['files'][:5], 1):
                size_mb = file['size'] / (1024 * 1024)
                print(f"  {i}. {file['key']}")
                print(f"     Size: {size_mb:.2f} MB")
                print(f"     Modified: {file['last_modified']}")
        else:
            print("⚠️  No CSV files found in the bucket")
    else:
        print(f"❌ List files failed: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Fetch latest file
print("\n📥 Test 2: Fetch and analyze latest CSV...")
print("⚠️  This may take a few minutes for large files...")

try:
    response = requests.post(
        "http://localhost:8000/api/aws/fetch",
        json={
            "access_key": access_key,
            "secret_key": secret_key,
            "region": region,
            "bucket_name": bucket,
            "prefix": prefix
        },
        timeout=300  # 5 minutes for large files
    )
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get('success'):
            print("✅ AWS CUR data fetched and analyzed successfully!")
            
            summary = data.get('summary', {})
            print(f"\n📊 Analysis Summary:")
            print(f"   Total Emissions: {summary.get('total_emissions_kg', 'N/A')} kg CO2e")
            print(f"   Total Cost: ${summary.get('total_cost', 'N/A')}")
            print(f"   Rows Analyzed: {summary.get('rows_analyzed', 'N/A')}")
            
            if 'service_breakdown' in data:
                print(f"\n🔧 Top Services by Emissions:")
                services = data['service_breakdown'].get('services', [])[:5]
                for svc in services:
                    print(f"   • {svc.get('service', 'N/A')}: {svc.get('emissions_kg', 0):.2f} kg CO2e")
        else:
            error = data.get('error', 'Unknown error')
            print(f"❌ Analysis failed: {error}")
    else:
        print(f"❌ Fetch failed: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except requests.exceptions.Timeout:
    print("⏱️  Request timed out - file might be too large")
    print("   Try using a smaller test file or increase timeout")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("✅ AWS S3 integration test complete!")
