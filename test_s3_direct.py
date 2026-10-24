import boto3
import os
from dotenv import load_dotenv

load_dotenv('cli/.env')

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='us-east-1'
)

print('Testing direct S3 access to carboniq-bucket...')
print('='*60)

try:
    # List all objects
    response = s3.list_objects_v2(Bucket='carboniq-bucket', MaxKeys=20)
    
    if 'Contents' in response:
        print(f'\n✅ Found {len(response["Contents"])} objects in bucket:\n')
        for obj in response['Contents']:
            size_kb = obj['Size'] / 1024
            print(f'  {obj["Key"]}')
            print(f'    Size: {size_kb:.1f} KB')
            print(f'    Modified: {obj["LastModified"]}')
            print()
    else:
        print('❌ Bucket is empty or no objects found')
        print('\nTrying to list with specific prefix...')
        
        # Try with carboniq-cur prefix
        response2 = s3.list_objects_v2(Bucket='carboniq-bucket', Prefix='carboniq-cur/', MaxKeys=20)
        if 'Contents' in response2:
            print(f'Found {len(response2["Contents"])} objects with prefix "carboniq-cur/"')
            for obj in response2['Contents'][:5]:
                print(f'  - {obj["Key"]}')
        else:
            print('No objects with prefix "carboniq-cur/"')
            
except Exception as e:
    print(f'❌ Error: {e}')
