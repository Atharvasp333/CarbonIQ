#!/usr/bin/env python3
"""
Test script to verify parser works with actual mock_csv.csv file
"""

import asyncio
import sys
sys.path.insert(0, 'backend')

from services.time_based_analyzer import analyze_csv_with_timestamps


async def test_actual_mock_csv():
    """Test with the actual mock_csv.csv file"""
    print("=" * 60)
    print("Testing with Actual mock_csv.csv File")
    print("=" * 60)
    
    try:
        # Read the actual mock CSV file
        with open('backend/data/mock_csv.csv', 'r') as f:
            csv_content = f.read()
        
        print(f"✓ Loaded mock_csv.csv ({len(csv_content)} bytes)")
        
        # Show first few lines
        lines = csv_content.split('\n')
        print(f"\nFirst 5 lines:")
        for line in lines[:5]:
            print(f"  {line}")
        
        # Count rows
        row_count = len(lines) - 1  # Exclude header
        print(f"\nTotal rows: {row_count}")
        
        # Analyze with time-based logic
        print("\nAnalyzing...")
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
        print(f"  Success Rate: {(result.processed_rows / row_count * 100):.1f}%")
        
        print(f"\n🔥 Top 5 Services by Emissions:")
        for item in result.by_service[:5]:
            print(f"  {item['service']:15} {item['co2_kg']:8.4f} kg CO₂  ({item['energy_kwh']:8.4f} kWh)")
        
        print(f"\n🌍 Top 5 Regions by Emissions:")
        for item in result.by_region[:5]:
            print(f"  {item['region']:15} {item['co2_kg']:8.4f} kg CO₂  (Avg: {item['avg_carbon_intensity']} gCO₂/kWh)")
        
        print(f"\n⏰ First 5 Time Periods:")
        for item in result.by_time[:5]:
            print(f"  {item['timestamp']:20} {item['co2_kg']:8.4f} kg CO₂  ({item['avg_carbon_intensity']} gCO₂/kWh)")
        
        print(f"\n📋 Sample Line Items (first 3):")
        for item in result.line_items[:3]:
            print(f"  {item.service:10} in {item.region:15} at {item.timestamp}")
            print(f"    Usage: {item.usage_amount:8.2f}, Intensity: {item.carbon_intensity} gCO₂/kWh")
            print(f"    CO₂: {item.co2_kg:.6f} kg, Cost: ${item.cost:.2f}, Source: {item.source}")
        
        # Verify services detected
        services_detected = set(item['service'] for item in result.by_service)
        print(f"\n✓ Services Detected: {', '.join(sorted(services_detected))}")
        
        # Verify regions detected
        regions_detected = set(item['region'] for item in result.by_region)
        print(f"✓ Regions Detected: {', '.join(sorted(regions_detected))}")
        
        print(f"\n✅ Actual CSV test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Actual CSV test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run test"""
    print("\n🧪 Actual CSV File Test\n")
    
    result = await test_actual_mock_csv()
    
    print("\n" + "=" * 60)
    if result:
        print("✅ Test PASSED - Parser works with actual CSV!")
        return 0
    else:
        print("❌ Test FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
