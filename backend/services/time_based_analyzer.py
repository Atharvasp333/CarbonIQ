import csv
import io
import logging
from datetime import datetime
from typing import List, Dict, Optional
from models.schemas import TimeBasedLineItem, TimeBasedAnalysisResponse
from services.electricity_maps import get_electricity_maps_client

logger = logging.getLogger(__name__)

# Service usage to kWh conversion factors
SERVICE_POWER_FACTORS = {
    "EC2": 0.15,           # kWh per hour
    "RDS": 0.12,           # kWh per hour
    "Lambda": 0.0000001,   # kWh per GB-second
    "S3": 0.0000005,       # kWh per GB-hour
    "EBS": 0.002,          # kWh per GB-hour
    "ECS": 0.10,           # kWh per hour
    "EKS": 0.10,           # kWh per hour
    "DynamoDB": 0.001,     # kWh per request
    "CloudFront": 0.0001,  # kWh per GB
    "ElastiCache": 0.08,   # kWh per hour
    "Redshift": 0.20,      # kWh per hour
    "SageMaker": 0.18,     # kWh per hour (ML training/inference)
    "Default": 0.05,       # Default factor
}


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Parse timestamp from various formats"""
    if not timestamp_str:
        return None
    
    # Try different formats
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str, fmt)
        except ValueError:
            continue
    
    logger.warning(f"Could not parse timestamp: {timestamp_str}")
    return None


def extract_service_name(product_name: str) -> str:
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
    elif "DYNAMODB" in product_upper:
        return "DynamoDB"
    elif "CLOUDFRONT" in product_upper:
        return "CloudFront"
    elif "ELASTICACHE" in product_upper:
        return "ElastiCache"
    elif "REDSHIFT" in product_upper:
        return "Redshift"
    else:
        return product_name[:20]


async def analyze_csv_with_timestamps(csv_content: str) -> TimeBasedAnalysisResponse:
    """
    Analyze AWS CSV data with time-based carbon intensity from Electricity Maps.
    
    This is the CORE function that implements time-based emission calculation.
    """
    logger.info("Starting time-based CSV analysis")
    
    # Get Electricity Maps client
    em_client = get_electricity_maps_client()
    
    # Parse CSV
    reader = csv.DictReader(io.StringIO(csv_content))
    line_items: List[TimeBasedLineItem] = []
    
    skipped_rows = 0
    processed_rows = 0
    
    for row_num, row in enumerate(reader, start=1):
        try:
            # Extract fields (handle different column names)
            # NEW FORMAT: Service, Region, UsageType, UsageAmount, Cost, Timestamp
            # OLD FORMAT: product/ProductName, product/region, lineItem/UsageAmount, etc.
            service = extract_service_name(
                row.get("Service") or 
                row.get("service") or 
                row.get("product/ProductName") or 
                ""
            )
            
            region = (
                row.get("Region") or 
                row.get("region") or 
                row.get("product/region") or 
                "UNKNOWN"
            )
            
            # Get usage type (new field)
            usage_type = (
                row.get("UsageType") or
                row.get("lineItem/UsageType") or
                ""
            )
            
            # Parse usage amount
            usage_str = (
                row.get("UsageAmount") or 
                row.get("usage") or 
                row.get("lineItem/UsageAmount") or 
                "0"
            )
            
            try:
                usage_amount = float(usage_str)
            except ValueError:
                logger.warning(f"Row {row_num}: Invalid usage amount '{usage_str}', skipping")
                skipped_rows += 1
                continue
            
            if usage_amount <= 0:
                skipped_rows += 1
                continue
            
            # Parse timestamp (CRITICAL)
            timestamp_str = (
                row.get("Timestamp") or
                row.get("timestamp") or
                row.get("lineItem/UsageStartDate") or
                row.get("StartTime") or
                ""
            )
            
            timestamp = parse_timestamp(timestamp_str)
            if not timestamp:
                logger.warning(f"Row {row_num}: Invalid timestamp '{timestamp_str}', skipping")
                skipped_rows += 1
                continue
            
            # Parse cost (optional)
            cost_str = (
                row.get("Cost") or 
                row.get("cost") or 
                row.get("lineItem/UnblendedCost") or 
                "0"
            )
            
            try:
                cost = float(cost_str)
            except ValueError:
                cost = 0.0
            
            # Map region to Electricity Maps zone
            zone = em_client.map_region_to_zone(region)
            
            # Get historical carbon intensity for this specific timestamp
            carbon_intensity, source = await em_client.get_historical_carbon_intensity(
                zone, 
                timestamp
            )
            
            # Convert usage to energy (kWh)
            power_factor = SERVICE_POWER_FACTORS.get(service, SERVICE_POWER_FACTORS["Default"])
            energy_kwh = usage_amount * power_factor
            
            # Calculate CO2 emissions
            # carbon_intensity is in gCO2/kWh, convert to kg
            co2_kg = (energy_kwh * carbon_intensity) / 1000
            
            # Create line item
            line_items.append(TimeBasedLineItem(
                service=service,
                region=region,
                zone=zone,
                usage_amount=usage_amount,
                timestamp=timestamp.isoformat(),
                carbon_intensity=round(carbon_intensity, 2),
                energy_kwh=round(energy_kwh, 6),
                co2_kg=round(co2_kg, 6),
                cost=round(cost, 2),
                source=source
            ))
            
            processed_rows += 1
            
        except Exception as e:
            logger.error(f"Row {row_num}: Error processing - {e}")
            skipped_rows += 1
            continue
    
    logger.info(f"Processed {processed_rows} rows, skipped {skipped_rows} rows")
    
    # Aggregate results
    return _aggregate_time_based_results(line_items, processed_rows, skipped_rows)


def _aggregate_time_based_results(
    line_items: List[TimeBasedLineItem],
    processed_rows: int,
    skipped_rows: int
) -> TimeBasedAnalysisResponse:
    """Aggregate time-based analysis results"""
    
    if not line_items:
        return _empty_time_based_response(processed_rows, skipped_rows)
    
    # Calculate totals
    total_co2 = sum(item.co2_kg for item in line_items)
    total_cost = sum(item.cost for item in line_items)
    total_energy = sum(item.energy_kwh for item in line_items)
    
    # Aggregate by service
    by_service = {}
    for item in line_items:
        if item.service not in by_service:
            by_service[item.service] = {
                "service": item.service,
                "co2_kg": 0,
                "energy_kwh": 0,
                "cost": 0
            }
        by_service[item.service]["co2_kg"] += item.co2_kg
        by_service[item.service]["energy_kwh"] += item.energy_kwh
        by_service[item.service]["cost"] += item.cost
    
    # Aggregate by region
    by_region = {}
    for item in line_items:
        if item.region not in by_region:
            by_region[item.region] = {
                "region": item.region,
                "zone": item.zone,
                "co2_kg": 0,
                "energy_kwh": 0,
                "avg_carbon_intensity": 0
            }
        by_region[item.region]["co2_kg"] += item.co2_kg
        by_region[item.region]["energy_kwh"] += item.energy_kwh
    
    # Calculate average carbon intensity per region
    for region_data in by_region.values():
        if region_data["energy_kwh"] > 0:
            region_data["avg_carbon_intensity"] = round(
                (region_data["co2_kg"] * 1000) / region_data["energy_kwh"], 
                2
            )
    
    # Aggregate by time (hour)
    by_time = {}
    for item in line_items:
        # Group by hour
        dt = datetime.fromisoformat(item.timestamp)
        time_key = dt.strftime("%Y-%m-%d %H:00")
        
        if time_key not in by_time:
            by_time[time_key] = {
                "timestamp": time_key,
                "co2_kg": 0,
                "energy_kwh": 0,
                "avg_carbon_intensity": 0
            }
        by_time[time_key]["co2_kg"] += item.co2_kg
        by_time[time_key]["energy_kwh"] += item.energy_kwh
    
    # Calculate average carbon intensity per time period
    for time_data in by_time.values():
        if time_data["energy_kwh"] > 0:
            time_data["avg_carbon_intensity"] = round(
                (time_data["co2_kg"] * 1000) / time_data["energy_kwh"], 
                2
            )
    
    # Round values
    for s in by_service.values():
        s["co2_kg"] = round(s["co2_kg"], 4)
        s["energy_kwh"] = round(s["energy_kwh"], 4)
        s["cost"] = round(s["cost"], 2)
    
    for r in by_region.values():
        r["co2_kg"] = round(r["co2_kg"], 4)
        r["energy_kwh"] = round(r["energy_kwh"], 4)
    
    for t in by_time.values():
        t["co2_kg"] = round(t["co2_kg"], 4)
        t["energy_kwh"] = round(t["energy_kwh"], 4)
    
    # Sort
    by_service_list = sorted(by_service.values(), key=lambda x: x["co2_kg"], reverse=True)
    by_region_list = sorted(by_region.values(), key=lambda x: x["co2_kg"], reverse=True)
    by_time_list = sorted(by_time.values(), key=lambda x: x["timestamp"])
    
    # Find tops
    top_service = by_service_list[0]["service"] if by_service_list else "Unknown"
    top_region = by_region_list[0]["region"] if by_region_list else "Unknown"
    
    # Calculate API usage stats
    em_client = get_electricity_maps_client()
    cache_stats = em_client.get_cache_stats()
    
    # Count sources
    api_calls = sum(1 for item in line_items if item.source == "electricity_maps")
    cached_calls = sum(1 for item in line_items if item.source == "electricity_maps_cached")
    fallback_calls = sum(1 for item in line_items if item.source == "fallback")
    
    return TimeBasedAnalysisResponse(
        total_co2_kg=round(total_co2, 4),
        total_cost=round(total_cost, 2),
        total_energy_kwh=round(total_energy, 4),
        top_region=top_region,
        top_service=top_service,
        by_service=by_service_list,
        by_region=by_region_list,
        by_time=by_time_list,
        line_items=line_items[:100],  # Limit to first 100 for display
        processed_rows=processed_rows,
        skipped_rows=skipped_rows,
        api_calls=api_calls,
        cached_calls=cached_calls,
        fallback_calls=fallback_calls,
        cache_size=cache_stats["cache_size"]
    )


def _empty_time_based_response(processed_rows: int, skipped_rows: int) -> TimeBasedAnalysisResponse:
    """Return empty response when no data"""
    return TimeBasedAnalysisResponse(
        total_co2_kg=0,
        total_cost=0,
        total_energy_kwh=0,
        top_region="None",
        top_service="None",
        by_service=[],
        by_region=[],
        by_time=[],
        line_items=[],
        processed_rows=processed_rows,
        skipped_rows=skipped_rows,
        api_calls=0,
        cached_calls=0,
        fallback_calls=0,
        cache_size=0
    )


def generate_demo_csv() -> str:
    """Generate demo CSV with timestamps for testing (NEW FORMAT)"""
    return """Service,Region,UsageType,UsageAmount,Cost,Timestamp
AmazonEC2,us-east-1,Compute,24.00,12.50,2024-01-15 14:00:00
AmazonEC2,us-west-2,Compute,48.00,8.75,2024-01-15 15:00:00
AmazonS3,us-east-1,Storage,1500.00,2.30,2024-01-15 16:00:00
AWSLambda,us-west-2,GB-Seconds,50.00,0.85,2024-01-15 17:00:00
AmazonEC2,eu-west-1,Compute,24.00,25.00,2024-01-15 18:00:00
AmazonS3,ap-south-1,Storage,500.00,5.00,2024-01-15 19:00:00
AmazonEC2,ap-south-1,Compute,24.00,11.50,2024-01-15 20:00:00
AmazonSageMaker,us-east-1,Compute,12.00,28.40,2024-01-15 21:00:00
AmazonEC2,us-east-2,Compute,24.00,18.00,2024-01-15 22:00:00
AmazonS3,eu-west-1,Storage,2500.00,3.75,2024-01-15 23:00:00
AWSLambda,us-east-1,GB-Seconds,75.00,1.25,2024-01-16 00:00:00
AmazonEC2,ap-northeast-1,Compute,48.00,9.20,2024-01-16 01:00:00
AmazonEC2,us-east-1,Compute,24.00,13.80,2024-01-16 02:00:00
AmazonSageMaker,us-west-1,Compute,18.00,8.00,2024-01-16 03:00:00
AWSLambda,eu-west-1,Requests,800.00,4.50,2024-01-16 04:00:00"""
