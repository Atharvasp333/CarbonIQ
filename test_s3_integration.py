"""
Test script to verify S3 integration fixes
"""
import asyncio
import sys
sys.path.insert(0, 'backend')

from services.s3_fetcher import fetch_csv_from_s3

async def test_s3_fetch():
    print("🧪 Testing S3 Integration...")
    print("-" * 50)
    
    # Your credentials
    access_key = "AKIA3DMB2ZT7KQQ5FAVF"
    secret_key = "tNYUCog+GDICn1lHlTe85b26+tuBzcKl0wXIVN3F"
    region = "ap-south-1"
    bucket_name = "carboniq-cur-bucket"
    
    print(f"📦 Bucket: {bucket_name}")
    print(f"🌍 Region: {region}")
    print()
    
    # Test 1: Auto-fetch latest file
    print("Test 1: Auto-fetch latest file from entire bucket")
    print("-" * 50)
    csv_content, error = await fetch_csv_from_s3(
        access_key=access_key,
        secret_key=secret_key,
        region=region,
        bucket_name=bucket_name,
        file_key=None  # Auto-discover
    )
    
    if error:
        print(f"❌ Error: {error}")
    else:
        print(f"✅ Success! Fetched {len(csv_content)} bytes")
        print(f"📄 First 200 characters:")
        print(csv_content[:200])
        print()
    
    # Test 2: Search in specific folder
    print("\nTest 2: Search in 'reports/CUR_report/' folder")
    print("-" * 50)
    csv_content, error = await fetch_csv_from_s3(
        access_key=access_key,
        secret_key=secret_key,
        region=region,
        bucket_name=bucket_name,
        file_key="reports/CUR_report/"  # Folder prefix
    )
    
    if error:
        print(f"❌ Error: {error}")
    else:
        print(f"✅ Success! Fetched {len(csv_content)} bytes")
        print(f"📄 First 200 characters:")
        print(csv_content[:200])
        print()
    
    # Test 3: Exact file path
    print("\nTest 3: Fetch exact file path")
    print("-" * 50)
    csv_content, error = await fetch_csv_from_s3(
        access_key=access_key,
        secret_key=secret_key,
        region=region,
        bucket_name=bucket_name,
        file_key="reports/CUR_report/20260501-20260601/CUR_report-00001.csv.gz"
    )
    
    if error:
        print(f"❌ Error: {error}")
    else:
        print(f"✅ Success! Fetched {len(csv_content)} bytes")
        lines = csv_content.split('\n')
        print(f"📊 Total lines: {len(lines)}")
        print(f"📄 First line (headers):")
        print(lines[0][:200] if lines else "No content")
        print()
        print(f"📄 Second line (first data row):")
        print(lines[1][:200] if len(lines) > 1 else "No data")

if __name__ == "__main__":
    asyncio.run(test_s3_fetch())
