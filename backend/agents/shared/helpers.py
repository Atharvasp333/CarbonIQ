"""
SHARED HELPER FUNCTIONS
Common utilities used by both engines
"""
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def parse_float(value: str) -> float:
    """Safely parse float from string"""
    try:
        return float(value) if value else 0.0
    except (ValueError, TypeError):
        return 0.0


def parse_timestamp(ts: str) -> str:
    """Parse and normalize timestamp to ISO format (hourly)"""
    if not ts:
        return datetime.utcnow().replace(minute=0, second=0, microsecond=0).isoformat()
    try:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        return dt.replace(minute=0, second=0, microsecond=0).isoformat()
    except Exception:
        return datetime.utcnow().replace(minute=0, second=0, microsecond=0).isoformat()


def extract_service_name(product_name: str) -> str:
    """Extract standardized service name from AWS product name"""
    product_upper = product_name.upper()
    service_map = {
        'EC2': ['EC2', 'ELASTIC COMPUTE', 'AMAZONEC2'],
        'Lambda': ['LAMBDA', 'AWSLAMBDA'],
        'S3': ['S3', 'SIMPLE STORAGE', 'AMAZONS3'],
        'RDS': ['RDS', 'RELATIONAL DATABASE', 'AMAZONRDS'],
        'SageMaker': ['SAGEMAKER', 'AMAZONSAGEMAKER'],
        'EBS': ['EBS', 'ELASTIC BLOCK'],
        'ECS': ['ECS', 'ELASTIC CONTAINER SERVICE'],
        'EKS': ['EKS', 'ELASTIC KUBERNETES'],
        'DynamoDB': ['DYNAMODB', 'AMAZONDYNAMODB'],
        'CloudFront': ['CLOUDFRONT', 'AMAZONCLOUDFRONT'],
        'ElastiCache': ['ELASTICACHE', 'AMAZONELASTICACHE'],
        'CloudWatch': ['CLOUDWATCH'],
        'Glue': ['GLUE', 'AWSGLUE'],
        'Amplify': ['AMPLIFY', 'AWSAMPLIFY'],
        'EFS': ['EFS', 'ELASTIC FILE SYSTEM', 'AMAZONEFS'],
        'API Gateway': ['API GATEWAY', 'AMAZONAPIGATEWAY', 'APIGATEWAY'],
        'DataZone': ['DATAZONE', 'AMAZONDATAZONE'],
        'Cognito': ['COGNITO', 'AMAZONCOGNITO'],
        'SNS': ['SNS', 'SIMPLE NOTIFICATION', 'AMAZONSNS'],
    }
    for service, keywords in service_map.items():
        if any(k in product_upper for k in keywords):
            return service
    return product_name[:25]


def normalize_region(region: str) -> str:
    """Normalize AWS region code"""
    region = (region or '').strip().lower()
    if not region or region in ('', 'global', 'n/a', 'none', 'any'):
        return 'global'
    if region.count('-') >= 2:
        return region
    region_map = {
        'us east': 'us-east-1', 'us west': 'us-west-1',
        'eu west': 'eu-west-1', 'eu central': 'eu-central-1',
        'asia pacific': 'ap-southeast-1', 'mumbai': 'ap-south-1',
    }
    for key, value in region_map.items():
        if key in region:
            return value
    return region


def get_location_name(region: str) -> str:
    """Get human-readable location name for region"""
    location_names = {
        'us-east-1': 'Virginia',
        'us-east-2': 'Ohio',
        'us-west-1': 'California',
        'us-west-2': 'Oregon',
        'eu-west-1': 'Ireland',
        'eu-west-2': 'London',
        'eu-west-3': 'Paris',
        'eu-central-1': 'Frankfurt',
        'eu-north-1': 'Stockholm',
        'eu-south-1': 'Milan',
        'ap-south-1': 'Mumbai',
        'ap-southeast-1': 'Singapore',
        'ap-southeast-2': 'Sydney',
        'ap-northeast-1': 'Tokyo',
        'ap-northeast-2': 'Seoul',
        'ap-northeast-3': 'Osaka',
        'ap-east-1': 'Hong Kong',
        'ca-central-1': 'Montreal',
        'sa-east-1': 'São Paulo',
        'me-south-1': 'Bahrain',
        'me-central-1': 'Tel Aviv',
        'af-south-1': 'Cape Town',
    }
    return location_names.get(region, region)
