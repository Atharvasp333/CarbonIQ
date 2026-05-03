#!/usr/bin/env python3
"""
Test script for AWS Integration feature
Run this to verify the backend is working correctly
"""

import asyncio
import sys
sys.path.insert(0, 'backend')

from services.aws_analyzer import parse_aws_csv, load_mock_data


async def test_demo_data():
    """Test loading and parsing demo data"""
    print("=" * 60)
    print("Testing Demo Data Loading")
    print("=" * 60)
    
    try:
        # Load mock CSV
        csv_content = load_mock_data()
        print(f"✓ Loaded mock CSV ({len(csv_content)} bytes)")
        
        # Parse and analyze
        result = await parse_aws_csv(csv_content)
        
        print(f"\n📊 Results:")
        print(f"  Total CO₂: {result.total_co2_kg} kg")
        print(f"  Total Cost: ${result.total_cost}")
        print(f"  Total Usage: {result.total_usage}")
        print(f"  Top Region: {result.top_region}")
        print(f"  Top Service: {result.top_service}")
        print(f"  Top Instance: {result.top_instance}")
        
        print(f"\n🔥 Emissions by Service:")
        for item in result.by_service[:5]:
            print(f"  {item['service']}: {item['co2_kg']} kg CO₂ (${item['cost']})")
        
        print(f"\n🌍 Emissions by Region:")
        for item in result.by_region[:5]:
            print(f"  {item['region']}: {item['co2_kg']} kg CO₂ (${item['cost']})")
        
        if result.idle_resources:
            print(f"\n⚠️  Idle Resources Detected:")
            for resource in result.idle_resources[:3]:
                print(f"  {resource['service']} in {resource['region']}: ${resource['cost']} (usage: {resource['usage']})")
        
        print(f"\n✅ Demo data test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Demo data test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_csv_parsing():
    """Test CSV parsing with various edge cases"""
    print("\n" + "=" * 60)
    print("Testing CSV Parsing Edge Cases")
    print("=" * 60)
    
    # Test with minimal CSV
    minimal_csv = """product/ProductName,product/region,lineItem/UsageAmount,lineItem/UnblendedCost
Amazon Elastic Compute Cloud,us-east-1,10,5.00"""
    
    try:
        result = await parse_aws_csv(minimal_csv)
        print(f"✓ Minimal CSV parsed: {result.total_co2_kg} kg CO₂")
    except Exception as e:
        print(f"❌ Minimal CSV failed: {e}")
        return False
    
    # Test with missing values
    missing_values_csv = """product/ProductName,product/region,lineItem/UsageAmount,lineItem/UnblendedCost
Amazon Elastic Compute Cloud,us-east-1,,5.00
Amazon Simple Storage Service,us-west-2,100,"""
    
    try:
        result = await parse_aws_csv(missing_values_csv)
        print(f"✓ Missing values handled: {len(result.line_items)} items parsed")
    except Exception as e:
        print(f"❌ Missing values test failed: {e}")
        return False
    
    # Test with empty CSV
    empty_csv = """product/ProductName,product/region,lineItem/UsageAmount,lineItem/UnblendedCost"""
    
    try:
        result = await parse_aws_csv(empty_csv)
        print(f"✓ Empty CSV handled: {result.total_co2_kg} kg CO₂")
    except Exception as e:
        print(f"❌ Empty CSV test failed: {e}")
        return False
    
    print(f"\n✅ CSV parsing tests PASSED")
    return True


async def main():
    """Run all tests"""
    print("\n🧪 AWS Integration Test Suite\n")
    
    tests = [
        test_demo_data(),
        test_csv_parsing(),
    ]
    
    results = await asyncio.gather(*tests)
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests PASSED!")
        return 0
    else:
        print("❌ Some tests FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
