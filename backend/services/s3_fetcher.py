import boto3
import logging
import gzip
import io
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


async def fetch_csv_from_s3(
    access_key: str,
    secret_key: str,
    region: str,
    bucket_name: str,
    file_key: Optional[str] = None
) -> Tuple[str, str]:
    """
    Fetch CSV from S3 bucket using provided credentials.
    
    Returns:
        Tuple[str, str]: (csv_content, error_message)
        If successful: (csv_content, None)
        If failed: (None, error_message)
    """
    try:
        # Create S3 client with provided credentials
        s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        # If no file_key provided, find the latest CSV file
        if not file_key:
            logger.info(f"No file key provided. Searching for latest CSV in bucket: {bucket_name}")
            file_key = await _find_latest_csv(s3_client, bucket_name)
            if not file_key:
                return None, "No CSV files found in the bucket"
        # If file_key ends with /, treat it as a prefix and find latest in that folder
        elif file_key.endswith('/'):
            logger.info(f"Prefix provided: {file_key}. Searching for latest CSV in this folder")
            file_key = await _find_latest_csv(s3_client, bucket_name, prefix=file_key)
            if not file_key:
                return None, f"No CSV files found in folder: {file_key}"
        
        # Fetch the file
        logger.info("="*80)
        logger.info(f"📦 FETCHING S3 FILE")
        logger.info(f"   Bucket: {bucket_name}")
        logger.info(f"   Region: {region}")
        logger.info(f"   File Key: {file_key}")
        logger.info("="*80)
        
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = response['Body'].read()
        file_size_mb = len(file_content) / (1024 * 1024)
        
        logger.info(f"✅ File downloaded: {len(file_content):,} bytes ({file_size_mb:.2f} MB)")
        
        # Decompress if it's a .gz file
        if file_key.lower().endswith('.gz'):
            logger.info(f"🗜️  Decompressing gzip file...")
            with gzip.GzipFile(fileobj=io.BytesIO(file_content)) as gz:
                csv_content = gz.read().decode('utf-8')
            decompressed_size_mb = len(csv_content) / (1024 * 1024)
            logger.info(f"✅ Decompressed: {len(csv_content):,} bytes ({decompressed_size_mb:.2f} MB)")
        else:
            csv_content = file_content.decode('utf-8')
            logger.info(f"📄 Plain CSV file (no compression)")
        
        # Count lines
        line_count = csv_content.count('\n')
        logger.info(f"📊 Total lines in CSV: {line_count:,}")
        logger.info("="*80)
        
        return csv_content, None
        
    except NoCredentialsError:
        error_msg = "Invalid AWS credentials: No credentials provided"
        logger.error(error_msg)
        return None, error_msg
    
    except PartialCredentialsError:
        error_msg = "Invalid AWS credentials: Incomplete credentials"
        logger.error(error_msg)
        return None, error_msg
    
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        
        if error_code == 'InvalidAccessKeyId':
            error_msg = "Invalid AWS credentials: Access Key ID not recognized"
        elif error_code == 'SignatureDoesNotMatch':
            error_msg = "Invalid AWS credentials: Secret Access Key is incorrect"
        elif error_code == 'AccessDenied':
            error_msg = "Access denied: Check bucket permissions and credentials"
        elif error_code == 'NoSuchBucket':
            error_msg = f"Bucket '{bucket_name}' does not exist"
        elif error_code == 'NoSuchKey':
            error_msg = f"File '{file_key}' not found in bucket"
        else:
            error_msg = f"AWS Error: {error_code} - {str(e)}"
        
        logger.error(error_msg)
        return None, error_msg
    
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return None, error_msg


async def _find_latest_csv(s3_client, bucket_name: str, prefix: str = '') -> Optional[str]:
    """Find the latest CSV file in the bucket (supports .csv and .csv.gz)"""
    try:
        # List all objects in the bucket with optional prefix
        all_objects = []
        paginator = s3_client.get_paginator('list_objects_v2')
        
        pagination_config = {'Bucket': bucket_name}
        if prefix:
            pagination_config['Prefix'] = prefix
            logger.info(f"Searching in prefix: {prefix}")
        
        for page in paginator.paginate(**pagination_config):
            if 'Contents' in page:
                all_objects.extend(page['Contents'])
        
        if not all_objects:
            return None
        
        # Filter CSV files (including .csv.gz)
        csv_files = [
            obj for obj in all_objects
            if obj['Key'].lower().endswith('.csv') or obj['Key'].lower().endswith('.csv.gz')
        ]
        
        if not csv_files:
            logger.warning(f"No CSV or CSV.GZ files found in bucket (prefix: {prefix})")
            return None
        
        # Sort by last modified date and get the latest
        latest_file = sorted(csv_files, key=lambda x: x['LastModified'], reverse=True)[0]
        file_size_mb = latest_file.get('Size', 0) / (1024 * 1024)
        
        logger.info("🔍 CSV FILES FOUND:")
        logger.info(f"   Total CSV/CSV.GZ files: {len(csv_files)}")
        logger.info(f"   Latest file: {latest_file['Key']}")
        logger.info(f"   Last modified: {latest_file['LastModified']}")
        logger.info(f"   File size: {file_size_mb:.2f} MB")
        
        return latest_file['Key']
        
    except Exception as e:
        logger.error(f"Error listing bucket contents: {e}")
        return None
