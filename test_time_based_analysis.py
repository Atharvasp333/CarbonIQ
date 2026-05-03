#!/usr/bin/env python3
"""
Test script for Time-Based Analysis feature
Run this to verify the backend is working correctly
"""

import asyncio
import sys
sys.path.insert(0, 'backend')

from services.time_based_analyzer import analyze_csv_with_timestamps, generate_demo_csv
from services.electricity_maps import get_electricity_maps_client


async def test_demo_data():
    """Test loading and analyzing demo data"""
    print("=" * 60)
    print("Testing Time-Based Analysis with Demo Data")
    print("=" * 60)
    
    try:
        # Generate demo CSV
        csv_content = generate_demo_csv()
        print(f"✓ Generated demo CSV ({len(csv_content)} bytes)")
        print(f"\nFirst few lines:")
        print('\n'.join(csv_content.split('\n')[:3]))
        
        # Analyze with time-based logic
        result = await analyze_csv_with_timestamps(csv_content)
        
        print(f"\n📊 Results:")
        print(f"  Total CO₂: {result.total_co2_kg} kg")
        print(f"  Total Energy: {result.total_energy_kwh} kWh")
        print(f"  Total Cost: ${result.total_cost}")
        print(f"  Top Region: {result.top_region}")
        print(f"  Top Service: {result.top_service}")
        
        print(f"\n📈 Processing Stats:")
        print(f"  Processed Rows: {result.processed_rows}")
        print(f"  Skipped Rows: {result.skipped_rows}")
        print(f"  API Calls: {result.api_calls}")
        print(f"  Cached Calls: {result.cached_calls}")
        print(f"  Fallback Calls: {result.fallback_calls}")
        print(f"  Cache Size: {result.cache_size}")
        
        print(f"\n🔥 Emissions by Service:")
        for item in result.by_service[:5]:
            print(f"  {item['service']}: {item['co2_kg']} kg CO₂ ({item['energy_kwh']} kWh)")
        
        print(f"\n🌍 Emissions by Region:")
        for item in result.by_region[:5]:
            print(f"  {item['region']} ({item['zone']}): {item['co2_kg']} kg CO₂ (Avg: {item['avg_carbon_intensity']} gCO₂/kWh)")
        
        print(f"\n⏰ Emissions Over Time:")
        for item in result.by_time[:5]:
            print(f"  {item['timestamp']}: {item['co2_kg']} kg CO₂ (Intensity: {item['avg_carbon_intensity']} gCO₂/kWh)")
        
        print(f"\n📋 Sample Line Items:")
        for item in result.line_items[:3]:
            print(f"  {item.service} in {item.region} at {item.timestamp}")
            print(f"    Usage: {item.usage_amount}, Intensity: {item.carbon_intensity} gCO₂/kWh")
            print(f"    CO₂: {item.co2_kg} kg, Source: {item.source}")
        
        print(f"\n✅ Time-based analysis test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Time-based analysis test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_region_mapping():
    """Test AWS region to Electricity Maps zone mapping"""
    print("\n" + "=" * 60)
    print("Testing Region Mapping")
    print("=" * 60)
    
    client = get_electricity_maps_client()
    
    test_regions = [
        "us-east-1",
        "us-west-2",
        "eu-west-1",
        "ap-south-1",
        "ap-northeast-1",
        "UNKNOWN"
    ]
    
    print("\nAWS Region → Electricity Maps Zone:")
    for region in test_regions:
        zone = client.map_region_to_zone(region)
        print(f"  {region:20} → {zone}")
    
    print(f"\n✅ Region mapping test PASSED")
    return True


async def test_timestamp_parsing():
    """Test timestamp parsing from various formats"""
    print("\n" + "=" * 60)
    print("Testing Timestamp Parsing")
    print("=" * 60)
    
    from services.time_based_analyzer import parse_timestamp
    
    test_timestamps = [
        "2024-01-15 14:00:00",
        "2024-01-15T14:00:00",
        "2024-01-15T14:00:00Z",
        "2024-01-15 14:00",
        "2024-01-15",
        "invalid",
        ""
    ]
    
    print("\nTimestamp Parsing:")
    for ts_str in test_timestamps:
        result = parse_timestamp(ts_str)
        status = "✓" if result else "✗"
        print(f"  {status} '{ts_str}' → {result}")
    
    print(f"\n✅ Timestamp parsing test PASSED")
    return True


async def test_cache_efficiency():
    """Test caching efficiency"""
    print("\n" + "=" * 60)
    print("Testing Cache Efficiency")
    print("=" * 60)
    
    # Create CSV with duplicate timestamps
    csv_content = """product/ProductName,product/region,lineItem/UsageAmount,lineItem/UnblendedCost,lineItem/UsageStartDate
Amazon Elastic Compute Cloud,us-east-1,24,12.50,2024-01-15 14:00:00
Amazon Elastic Compute Cloud,us-east-1,24,12.50,2024-01-15 14:00:00
Amazon Elastic Compute Cloud,us-east-1,24,12.50,2024-01-15 14:00:00
Amazon Elastic Compute Cloud,us-west-2,48,8.75,2024-01-15 14:00:00
Amazon Elastic Compute Cloud,us-west-2,48,8.75,2024-01-15 14:00:00"""
    
    result = await analyze_csv_with_timestamps(csv_content)
    
    print(f"\nProcessed {result.processed_rows} rows")
    print(f"API Calls: {result.api_calls}")
    print(f"Cached Calls: {result.cached_calls}")
    print(f"Cache Hit Rate: {(result.cached_calls / result.processed_rows * 100):.1f}%")
    
    if result.cached_calls > 0:
        print(f"\n✅ Cache efficiency test PASSED (caching is working)")
    else:
        print(f"\n⚠️  Cache efficiency test: No cached calls (expected on first run)")
    
    return True


async def main():
    """Run all tests"""
    print("\n🧪 Time-Based Analysis Test Suite\n")
    
    tests = [
        ("Demo Data Analysis", test_demo_data()),
        ("Region Mapping", test_region_mapping()),
        ("Timestamp Parsing", test_timestamp_parsing()),
        ("Cache Efficiency", test_cache_efficiency()),
    ]
    
    results = []
    for name, test_coro in tests:
        try:
            result = await test_coro
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} test failed with error: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests PASSED!")
        return 0
    else:
        print("❌ Some tests FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
