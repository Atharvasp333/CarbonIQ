import boto3
import logging
import gzip
import zipfile
import io
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

        # Handle compressed files
        file_key_lower = file_key.lower()
        
        if file_key_lower.endswith('.csv.zip'):
            # Handle ZIP compressed files
            try:
                logger.info(f"Extracting CSV from ZIP archive: {file_key}")
                with zipfile.ZipFile(io.BytesIO(content_bytes)) as zip_file:
                    # Get list of files in the archive
                    file_list = zip_file.namelist()
                    
                    if not file_list:
                        return None, "ZIP archive is empty"
                    
                    # Find the first CSV file in the archive
                    csv_file = None
                    for filename in file_list:
                        if filename.lower().endswith('.csv'):
                            csv_file = filename
                            break
                    
                    if not csv_file:
                        return None, "No CSV file found in ZIP archive"
                    
                    logger.info(f"Extracting CSV file: {csv_file}")
                    content_bytes = zip_file.read(csv_file)
                    
                    if len(content_bytes) == 0:
                        return None, f"CSV file '{csv_file}' is empty"
                        
            except zipfile.BadZipFile:
                error_msg = f"Invalid ZIP file: {file_key}"
                logger.error(error_msg)
                return None, error_msg
            except Exception as e:
                error_msg = f"Error extracting ZIP file: {str(e)}"
                logger.error(error_msg)
                return None, error_msg
                
        elif file_key_lower.endswith('.gz'):
            # Handle gzip compressed files
            try:
                logger.info(f"Decompressing gzip file: {file_key}")
                content_bytes = gzip.decompress(content_bytes)
            except Exception as e:
                error_msg = f"Error decompressing gzip file: {str(e)}"
                logger.error(error_msg)
                return None, error_msg

        # Decode to UTF-8
        try:
            csv_content = content_bytes.decode('utf-8')
        except UnicodeDecodeError as e:
            error_msg = f"Error decoding CSV content: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
            
        if not csv_content.strip():
            return None, "CSV content is empty"
            
        logger.info(f"Successfully fetched and processed {len(csv_content)} bytes from S3")
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
    """Find the latest CSV file in the bucket (supports .csv, .csv.gz, and .csv.zip)"""
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' not in response:
            return None
        
        # Filter CSV files (including gzip and zip)
        csv_files = [
            obj for obj in response['Contents']
            if obj['Key'].lower().endswith(('.csv', '.csv.gz', '.csv.zip'))
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
