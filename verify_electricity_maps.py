#!/usr/bin/env python3
"""
Verification Tool: Check if Electricity Maps API is being used
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv('backend/.env')

sys.path.insert(0, 'backend')

from services.electricity_maps import get_electricity_maps_client
from datetime import datetime


async def verify_api_configuration():
    """Check if Electricity Maps API is configured"""
    print("=" * 60)
    print("Electricity Maps API Configuration Check")
    print("=" * 60)
    
    api_key = os.getenv("ELECTRICITY_MAPS_API_KEY")
    
    if not api_key:
        print("❌ No API key found in environment")
        print("   Set ELECTRICITY_MAPS_API_KEY in .env file")
        return False
    
    if api_key == "your_electricity_maps_api_key_here":
        print("❌ API key is placeholder value")
        print("   Replace with real API key in .env file")
        return False
    
    print(f"✓ API key found: {api_key[:10]}...{api_key[-4:]}")
    return True


async def test_api_call():
    """Test actual API call to Electricity Maps"""
    print("\n" + "=" * 60)
    print("Testing Actual API Call")
    print("=" * 60)
    
    client = get_electricity_maps_client()
    
    # Test with a specific zone and timestamp
    zone = "US-MIDA-PJM"  # Virginia
    timestamp = datetime(2024, 1, 15, 14, 0, 0)
    
    print(f"\nCalling Electricity Maps API:")
    print(f"  Zone: {zone}")
    print(f"  Timestamp: {timestamp}")
    
    try:
        intensity, source = await client.get_historical_carbon_intensity(zone, timestamp)
        
        print(f"\n📊 Result:")
        print(f"  Carbon Intensity: {intensity} gCO₂/kWh")
        print(f"  Source: {source}")
        
        if source == "electricity_maps":
            print(f"\n✅ SUCCESS! API is working and returning real data")
            return True
        elif source == "electricity_maps_cached":
            print(f"\n✅ SUCCESS! Using cached API data (API was called before)")
            return True
        elif source == "fallback":
            print(f"\n⚠️  WARNING! Using fallback values (API not working)")
            print(f"   Possible reasons:")
            print(f"   - Invalid API key")
            print(f"   - API rate limit exceeded")
            print(f"   - Network error")
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


async def test_with_csv_data():
    """Test with actual CSV data to see sources"""
    print("\n" + "=" * 60)
    print("Testing with CSV Data")
    print("=" * 60)
    
    from services.time_based_analyzer import analyze_csv_with_timestamps
    
    # Small test CSV
    csv_content = """Service,Region,UsageType,UsageAmount,Cost,Timestamp
AmazonEC2,us-east-1,Compute,24.00,12.50,2024-01-15 14:00:00
AmazonEC2,us-west-2,Compute,48.00,8.75,2024-01-15 15:00:00
AmazonS3,us-east-1,Storage,1500.00,2.30,2024-01-15 16:00:00"""
    
    print("\nAnalyzing 3 rows...")
    result = await analyze_csv_with_timestamps(csv_content)
    
    print(f"\n📊 Results:")
    print(f"  Processed Rows: {result.processed_rows}")
    print(f"  API Calls: {result.api_calls}")
    print(f"  Cached Calls: {result.cached_calls}")
    print(f"  Fallback Calls: {result.fallback_calls}")
    
    print(f"\n📋 Line Items with Sources:")
    for item in result.line_items:
        print(f"  {item.service:10} in {item.region:15} → Source: {item.source}")
    
    # Check if any API calls were made
    if result.api_calls > 0:
        print(f"\n✅ SUCCESS! Electricity Maps API is being used")
        print(f"   {result.api_calls} API calls made")
        return True
    elif result.cached_calls > 0:
        print(f"\n✅ SUCCESS! Using cached Electricity Maps data")
        print(f"   {result.cached_calls} cached results used")
        return True
    else:
        print(f"\n⚠️  WARNING! All results are from fallback calculations")
        print(f"   API is not being used")
        return False


async def show_comparison():
    """Show comparison between API and fallback values"""
    print("\n" + "=" * 60)
    print("Comparison: API vs Fallback Values")
    print("=" * 60)
    
    from services.electricity_maps import FALLBACK_CARBON_INTENSITY
    
    print("\nFallback values (used when API fails):")
    for zone, intensity in list(FALLBACK_CARBON_INTENSITY.items())[:10]:
        print(f"  {zone:20} {intensity:6} gCO₂/kWh")
    
    print("\nIf you see these exact values in your results,")
    print("it means the API is NOT being used.")
    print("\nIf you see different values, the API IS working!")


async def main():
    """Run all verification checks"""
    print("\n🔍 Electricity Maps API Verification Tool\n")
    
    # Check 1: API Configuration
    config_ok = await verify_api_configuration()
    
    if not config_ok:
        print("\n" + "=" * 60)
        print("❌ API not configured properly")
        print("=" * 60)
        print("\nTo fix:")
        print("1. Get API key from https://www.electricitymaps.com/")
        print("2. Add to backend/.env file:")
        print("   ELECTRICITY_MAPS_API_KEY=your_actual_key_here")
        return 1
    
    # Check 2: Test API Call
    api_ok = await test_api_call()
    
    # Check 3: Test with CSV Data
    csv_ok = await test_with_csv_data()
    
    # Check 4: Show Comparison
    await show_comparison()
    
    # Summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    print(f"\n{'✓' if config_ok else '✗'} API Configuration")
    print(f"{'✓' if api_ok else '✗'} API Call Test")
    print(f"{'✓' if csv_ok else '✗'} CSV Analysis Test")
    
    if config_ok and api_ok and csv_ok:
        print("\n✅ VERIFIED: Electricity Maps API is working!")
        print("\nYour emissions are being calculated using:")
        print("  • Real historical carbon intensity data")
        print("  • From Electricity Maps API")
        print("  • Not just static math calculations")
        return 0
    else:
        print("\n⚠️  WARNING: API is not working properly")
        print("\nYour emissions are being calculated using:")
        print("  • Fallback static values")
        print("  • Mathematical calculations only")
        print("  • Not real-time API data")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
