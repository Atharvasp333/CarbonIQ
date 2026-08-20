import csv
import io
import logging
from typing import List
from models.schemas import AWSLineItem, AWSAnalysisResponse

logger = logging.getLogger(__name__)

# Region emission factors (kg CO2 per kWh) - based on grid carbon intensity
REGION_EMISSION_FACTORS = {
    "us-east-1": 0.415,      # Virginia
    "us-east-2": 0.744,      # Ohio
    "us-west-1": 0.285,      # California
    "us-west-2": 0.285,      # Oregon
    "eu-west-1": 0.295,      # Ireland
    "eu-central-1": 0.338,   # Frankfurt
    "ap-south-1": 0.708,     # Mumbai
    "ap-southeast-1": 0.493, # Singapore
    "ap-northeast-1": 0.463, # Tokyo
}

# Service usage to kWh conversion (simplified)
SERVICE_POWER_FACTORS = {
    "EC2": 0.15,      # kWh per usage unit
    "RDS": 0.12,
    "Lambda": 0.0001,
    "S3": 0.0005,
    "EBS": 0.002,
    "ECS": 0.10,
    "EKS": 0.10,
    "SageMaker": 0.18,  # kWh per usage unit
}


async def parse_aws_csv(csv_content: str) -> AWSAnalysisResponse:
    """Parse AWS billing CSV and calculate carbon emissions"""
    
    reader = csv.DictReader(io.StringIO(csv_content))
    line_items: List[AWSLineItem] = []
    
    for row in reader:
        try:
            # Support both old and new CSV formats
            # NEW FORMAT: Service, Region, UsageAmount, Cost
            # OLD FORMAT: product/ProductName, product/region, lineItem/UsageAmount, lineItem/UnblendedCost
            
            service_name = (
                row.get("Service") or 
                row.get("service") or 
                row.get("product/ProductName") or 
                "Unknown"
            )
            service = _extract_service(service_name)
            
            region = (
                row.get("Region") or 
                row.get("region") or 
                row.get("product/region") or 
                "unknown"
            )
            
            usage_str = (
                row.get("UsageAmount") or 
                row.get("usage") or 
                row.get("lineItem/UsageAmount") or 
                "0"
            )
            usage_amount = float(usage_str) if usage_str else 0
            
            instance_type = (
                row.get("InstanceType") or 
                row.get("product/instanceType") or 
                None
            )
            
            cost_str = (
                row.get("Cost") or 
                row.get("cost") or 
                row.get("lineItem/UnblendedCost") or 
                "0"
            )
            cost = float(cost_str) if cost_str else 0
            
            # Calculate CO2
            co2_kg = _calculate_co2(service, region, usage_amount)
            
            if usage_amount > 0 or cost > 0:
                line_items.append(AWSLineItem(
                    service=service,
                    region=region,
                    usage_amount=usage_amount,
                    instance_type=instance_type,
                    cost=cost,
                    co2_kg=round(co2_kg, 4)
                ))
        except Exception as e:
            logger.warning(f"Skipping row due to error: {e}")
            continue
    
    return _aggregate_results(line_items)


def _extract_service(product_name: str) -> str:
    """Extract service name from AWS product name"""
    if not product_name:
        return "Unknown"
    
    product_upper = product_name.upper()
    
    # Handle new format: AWSLambda, AmazonEC2, AmazonS3, AmazonSageMaker
    if "LAMBDA" in product_upper or "AWSLAMBDA" in product_upper:
        return "Lambda"
    elif "EC2" in product_upper or "AMAZONEC2" in product_upper or "ELASTIC COMPUTE" in product_upper:
        return "EC2"
    elif "S3" in product_upper or "AMAZONS3" in product_upper or "SIMPLE STORAGE" in product_upper:
        return "S3"
    elif "SAGEMAKER" in product_upper or "AMAZONSAGEMAKER" in product_upper:
        return "SageMaker"
    elif "RDS" in product_upper or "RELATIONAL DATABASE" in product_upper:
        return "RDS"
    elif "EBS" in product_upper or "ELASTIC BLOCK" in product_upper:
        return "EBS"
    elif "ECS" in product_upper:
        return "ECS"
    elif "EKS" in product_upper:
        return "EKS"
    else:
        return product_name[:20]  # Truncate long names


def _calculate_co2(service: str, region: str, usage_amount: float) -> float:
    """Calculate CO2 emissions for a service usage"""
    # Get emission factor for region (default to 0.4 if unknown)
    emission_factor = REGION_EMISSION_FACTORS.get(region, 0.4)
    
    # Get power factor for service (default to 0.1 if unknown)
    power_factor = SERVICE_POWER_FACTORS.get(service, 0.1)
    
    # CO2 = usage × power_factor × emission_factor
    kwh = usage_amount * power_factor
    co2_kg = kwh * emission_factor
    
    return co2_kg


def _aggregate_results(line_items: List[AWSLineItem]) -> AWSAnalysisResponse:
    """Aggregate line items into summary statistics"""
    
    if not line_items:
        return _empty_response()
    
    total_co2 = sum(item.co2_kg for item in line_items)
    total_cost = sum(item.cost for item in line_items)
    total_usage = sum(item.usage_amount for item in line_items)
    
    # Aggregate by service
    by_service = {}
    for item in line_items:
        if item.service not in by_service:
            by_service[item.service] = {"service": item.service, "co2_kg": 0, "cost": 0, "usage": 0}
        by_service[item.service]["co2_kg"] += item.co2_kg
        by_service[item.service]["cost"] += item.cost
        by_service[item.service]["usage"] += item.usage_amount
    
    # Aggregate by region
    by_region = {}
    for item in line_items:
        if item.region not in by_region:
            by_region[item.region] = {"region": item.region, "co2_kg": 0, "cost": 0}
        by_region[item.region]["co2_kg"] += item.co2_kg
        by_region[item.region]["cost"] += item.cost
    
    # Aggregate by instance type
    by_instance = {}
    for item in line_items:
        if item.instance_type:
            if item.instance_type not in by_instance:
                by_instance[item.instance_type] = {"instance": item.instance_type, "co2_kg": 0, "cost": 0}
            by_instance[item.instance_type]["co2_kg"] += item.co2_kg
            by_instance[item.instance_type]["cost"] += item.cost
    
    # Round values
    for s in by_service.values():
        s["co2_kg"] = round(s["co2_kg"], 2)
        s["cost"] = round(s["cost"], 2)
        s["usage"] = round(s["usage"], 2)
    
    for r in by_region.values():
        r["co2_kg"] = round(r["co2_kg"], 2)
        r["cost"] = round(r["cost"], 2)
    
    for i in by_instance.values():
        i["co2_kg"] = round(i["co2_kg"], 2)
        i["cost"] = round(i["cost"], 2)
    
    # Sort by CO2
    by_service_list = sorted(by_service.values(), key=lambda x: x["co2_kg"], reverse=True)
    by_region_list = sorted(by_region.values(), key=lambda x: x["co2_kg"], reverse=True)
    by_instance_list = sorted(by_instance.values(), key=lambda x: x["co2_kg"], reverse=True)
    
    # Find tops
    top_service = by_service_list[0]["service"] if by_service_list else "Unknown"
    top_region = by_region_list[0]["region"] if by_region_list else "Unknown"
    top_instance = by_instance_list[0]["instance"] if by_instance_list else None
    
    # Detect idle resources (low usage but high cost)
    idle_resources = []
    for item in line_items:
        if item.cost > 5 and item.usage_amount < 1:
            idle_resources.append({
                "service": item.service,
                "region": item.region,
                "instance_type": item.instance_type,
                "cost": round(item.cost, 2),
                "usage": round(item.usage_amount, 2)
            })
    
    return AWSAnalysisResponse(
        total_co2_kg=round(total_co2, 2),
        total_cost=round(total_cost, 2),
        total_usage=round(total_usage, 2),
        top_region=top_region,
        top_service=top_service,
        top_instance=top_instance,
        by_service=by_service_list,
        by_region=by_region_list,
        by_instance=by_instance_list,
        line_items=line_items[:100],  # Limit to first 100 for display
        idle_resources=idle_resources[:10]
    )


def _empty_response() -> AWSAnalysisResponse:
    """Return empty response when no data"""
    return AWSAnalysisResponse(
        total_co2_kg=0,
        total_cost=0,
        total_usage=0,
        top_region="None",
        top_service="None",
        top_instance=None,
        by_service=[],
        by_region=[],
        by_instance=[],
        line_items=[],
        idle_resources=[]
    )


def load_mock_data() -> str:
    """Load mock CSV data for demo"""
    return """identity/LineItemId,bill/BillingPeriodStartDate,lineItem/UsageStartDate,lineItem/UsageEndDate,product/ProductName,product/region,lineItem/UsageType,lineItem/UsageAmount,product/instanceType,lineItem/ResourceId,lineItem/UnblendedCost
1,2024-01-01,2024-01-01,2024-01-02,Amazon Elastic Compute Cloud,us-east-1,BoxUsage:m5.large,24,m5.large,i-1234567890abcdef0,12.50
2,2024-01-01,2024-01-01,2024-01-02,Amazon Elastic Compute Cloud,us-west-2,BoxUsage:t3.medium,48,t3.medium,i-abcdef1234567890,8.75
3,2024-01-01,2024-01-01,2024-01-02,Amazon Relational Database Service,us-east-1,InstanceUsage:db.t3.small,24,db.t3.small,db-instance-1,15.20
4,2024-01-01,2024-01-01,2024-01-02,Amazon Simple Storage Service,us-east-1,TimedStorage-ByteHrs,1500000,,,2.30
5,2024-01-01,2024-01-01,2024-01-02,AWS Lambda,us-west-2,Lambda-GB-Second,50000,,,0.85
6,2024-01-01,2024-01-01,2024-01-02,Amazon Elastic Compute Cloud,eu-west-1,BoxUsage:m5.xlarge,24,m5.xlarge,i-fedcba0987654321,25.00
7,2024-01-01,2024-01-01,2024-01-02,Amazon Elastic Block Store,us-east-1,VolumeUsage,500,,,5.00
8,2024-01-01,2024-01-01,2024-01-02,Amazon Elastic Compute Cloud,ap-south-1,BoxUsage:t3.large,24,t3.large,i-mumbai123456,11.50
9,2024-01-01,2024-01-01,2024-01-02,Amazon Relational Database Service,us-west-2,InstanceUsage:db.m5.large,24,db.m5.large,db-instance-2,28.40
10,2024-01-01,2024-01-01,2024-01-02,Amazon Elastic Compute Cloud,us-east-2,BoxUsage:m5.large,2,m5.large,i-idle-resource,18.00
11,2024-01-01,2024-01-01,2024-01-02,Amazon Simple Storage Service,eu-west-1,TimedStorage-ByteHrs,2500000,,,3.75
12,2024-01-01,2024-01-01,2024-01-02,AWS Lambda,us-east-1,Lambda-GB-Second,75000,,,1.25
13,2024-01-01,2024-01-01,2024-01-02,Amazon Elastic Compute Cloud,ap-northeast-1,BoxUsage:t3.medium,48,t3.medium,i-tokyo123456,9.20
14,2024-01-01,2024-01-01,2024-01-02,Amazon Elastic Compute Cloud,us-east-1,BoxUsage:c5.large,24,c5.large,i-compute123,13.80
15,2024-01-01,2024-01-01,2024-01-02,Amazon Elastic Block Store,us-west-2,VolumeUsage,800,,,8.00"""
