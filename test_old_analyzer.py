#!/usr/bin/env python3
"""
Test the old aws_analyzer.py with new CSV format
"""

import asyncio
import sys
sys.path.insert(0, 'backend')

from services.aws_analyzer import parse_aws_csv


async def test_new_format():
    """Test with new CSV format"""
    print("=" * 60)
    print("Testing OLD Analyzer with NEW CSV Format")
    print("=" * 60)
    
    # Read the actual mock CSV file
    with open('backend/data/mock_csv.csv', 'r') as f:
        csv_content = f.read()
    
    print(f"✓ Loaded mock_csv.csv ({len(csv_content)} bytes)")
    
    # Show first few lines
    lines = csv_content.split('\n')
    print(f"\nFirst 3 lines:")
    for line in lines[:3]:
        print(f"  {line}")
    
    # Analyze
    print("\nAnalyzing...")
    result = await parse_aws_csv(csv_content)
    
    print(f"\n📊 Results:")
    print(f"  Total CO₂: {result.total_co2_kg} kg")
    print(f"  Total Cost: ${result.total_cost}")
    print(f"  Total Usage: {result.total_usage}")
    print(f"  Top Region: {result.top_region}")
    print(f"  Top Service: {result.top_service}")
    
    print(f"\n🔥 Top 5 Services:")
    for item in result.by_service[:5]:
        print(f"  {item['service']:15} {item['co2_kg']:8.2f} kg CO₂  (${item['cost']:.2f})")
    
    print(f"\n🌍 Top 5 Regions:")
    for item in result.by_region[:5]:
        print(f"  {item['region']:15} {item['co2_kg']:8.2f} kg CO₂  (${item['cost']:.2f})")
    
    if result.total_co2_kg > 0:
        print(f"\n✅ Test PASSED - Parser working with new format!")
        return True
    else:
        print(f"\n❌ Test FAILED - No emissions calculated")
        return False


async def main():
    result = await test_new_format()
    return 0 if result else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
