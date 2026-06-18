import boto3
import logging
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


async def fetch_csv_from_s3(
    access_key: str,
    secret_key: str,
    region: str,
    bucket_name: str,
    file_key: Optional[str] = None,
    verify_only: bool = False,
) -> Tuple[str, str]:
    """
    Fetch CSV from S3 bucket using provided credentials.

    If verify_only=True, only list the bucket (no download) — used to validate credentials.

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

        # verify_only: just confirm we can list the bucket
        if verify_only:
            s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
            return None, None

        # If no file_key provided, find the latest CSV file
        if not file_key:
            logger.info(f"No file key provided. Searching for latest CSV in bucket: {bucket_name}")
            file_key = await _find_latest_csv(s3_client, bucket_name)
            if not file_key:
                return None, "No CSV files found in the bucket"

        # Fetch the file
        logger.info(f"Fetching file: {file_key} from bucket: {bucket_name}")
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        content_bytes = response['Body'].read()

        # Handle gzip compressed files
        if file_key.lower().endswith('.gz'):
            import gzip
            content_bytes = gzip.decompress(content_bytes)

        csv_content = content_bytes.decode('utf-8')
        logger.info(f"Successfully fetched {len(csv_content)} bytes from S3")
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


async def _find_latest_csv(s3_client, bucket_name: str) -> Optional[str]:
    """Find the latest CSV file in the bucket"""
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' not in response:
            return None
        
        # Filter CSV files (including gzip)
        csv_files = [
            obj for obj in response['Contents']
            if obj['Key'].lower().endswith('.csv') or obj['Key'].lower().endswith('.csv.gz')
        ]
        
        if not csv_files:
            return None
        
        # Sort by last modified date and get the latest
        latest_file = sorted(csv_files, key=lambda x: x['LastModified'], reverse=True)[0]
        logger.info(f"Found latest CSV: {latest_file['Key']}")
        return latest_file['Key']
        
    except Exception as e:
        logger.error(f"Error listing bucket contents: {e}")
        return None
