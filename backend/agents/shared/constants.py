"""
SHARED CONSTANTS
Used by both Carbon Accounting and Sustainability Intelligence engines
"""

# AWS Region to Electricity Maps Zone mapping
AWS_REGION_ZONE_MAP = {
    # US Regions
    'us-east-1': 'US-MIDA-PJM',
    'us-east-2': 'US-MIDW-MISO',
    'us-west-1': 'US-CAL-CISO',
    'us-west-2': 'US-NW-PACW',
    
    # Global/Unknown
    'global': 'US-MIDA-PJM',
    
    # EU Regions
    'eu-west-1': 'IE',
    'eu-west-2': 'GB',
    'eu-west-3': 'FR',
    'eu-central-1': 'DE',
    'eu-north-1': 'SE',
    'eu-south-1': 'IT-NO',
    
    # Asia Pacific
    'ap-south-1': 'IN-WE',
    'ap-southeast-1': 'SG',
    'ap-southeast-2': 'AU-NSW',
    'ap-northeast-1': 'JP-TK',
    'ap-northeast-2': 'KR',
    'ap-northeast-3': 'JP-KN',
    'ap-east-1': 'HK',
    
    # Canada
    'ca-central-1': 'CA-ON',
    
    # South America
    'sa-east-1': 'BR-CS',
    
    # Middle East
    'me-south-1': 'BH',
    'me-central-1': 'IL',
    
    # Africa
    'af-south-1': 'ZA',
}

# Fallback carbon intensity values (gCO2/kWh)
FALLBACK_CARBON_INTENSITY = {
    "US-MIDA-PJM": 420, "US-MIDW-MISO": 500, "US-CAL-CISO": 285,
    "US-NW-PACW": 200, "IE": 295, "GB": 230, "FR": 60, "DE": 350,
    "SE": 40, "IT-NO": 300, "IN-WE": 708, "IN": 708,
    "JP-TK": 463, "KR": 450, "JP-KN": 463, "SG": 493,
    "AU-NSW": 700, "HK": 650, "BR-CS": 100, "CA-ON": 120,
    "AE": 500, "ZA": 850, "UNKNOWN": 450,
}

# Service-specific energy estimation factors (kWh conversion)
SERVICE_ENERGY_FACTORS = {
    'EC2': {
        'unit': 'hours',
        'base_factor': 0.15,
        'instance_multipliers': {
            'nano': 0.1, 'micro': 0.2, 'small': 0.3, 'medium': 0.5,
            'large': 1.0, 'xlarge': 2.0, '2xlarge': 4.0, '4xlarge': 8.0,
            '8xlarge': 16.0, '12xlarge': 24.0, '16xlarge': 32.0, '24xlarge': 48.0,
        }
    },
    'RDS': {
        'unit': 'hours',
        'base_factor': 0.12,
        'instance_multipliers': {
            'micro': 0.15, 'small': 0.25, 'medium': 0.4, 'large': 0.8,
            'xlarge': 1.6, '2xlarge': 3.2, '4xlarge': 6.4, '8xlarge': 12.8,
        }
    },
    'SageMaker': {
        'unit': 'hours',
        'base_factor': 0.18,
        'instance_multipliers': {
            'medium': 0.5, 'large': 1.0, 'xlarge': 2.5, '2xlarge': 5.0,
            '4xlarge': 10.0, '8xlarge': 20.0,
        }
    },
    'ECS': {'unit': 'hours', 'base_factor': 0.10},
    'EKS': {'unit': 'hours', 'base_factor': 0.10},
    'ElastiCache': {'unit': 'hours', 'base_factor': 0.08},
    'Lambda': {'unit': 'gb-seconds', 'base_factor': 0.0001},
    'S3': {'unit': 'gb-hours', 'base_factor': 0.0000005},
    'EBS': {'unit': 'gb-hours', 'base_factor': 0.000002},
    'DynamoDB': {'unit': 'requests', 'base_factor': 0.00000001},
    'CloudFront': {'unit': 'gb', 'base_factor': 0.0001},
    'CloudWatch': {'unit': 'requests', 'base_factor': 0.000001},
    'Glue': {'unit': 'hours', 'base_factor': 0.10},
    'Amplify': {'unit': 'hours', 'base_factor': 0.05},
    'EFS': {'unit': 'gb-hours', 'base_factor': 0.000002},
    'API Gateway': {'unit': 'requests', 'base_factor': 0.000001},
    'DataZone': {'unit': 'hours', 'base_factor': 0.08},
    'Cognito': {'unit': 'requests', 'base_factor': 0.0000001},
    'SNS': {'unit': 'requests', 'base_factor': 0.0000001},
}

# Required CUR columns
REQUIRED_CUR_COLUMNS = {
    'product/ProductName',
    'lineItem/UsageStartDate',
    'lineItem/UsageAmount',
    'lineItem/UnblendedCost'
}

# Line items to skip in CUR processing
SKIP_LINE_ITEM_TYPES = ('Tax', 'Credit', 'Refund', 'Fee')
