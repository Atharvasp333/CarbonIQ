import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('cli/.env')

print("Fetching AWS CUR file from S3...")
print("File: carboniq-cur-00001.csv.zip")
print("="*60)

response = requests.post(
    'http://localhost:8000/api/aws/fetch',
    json={
        'access_key': os.getenv('AWS_ACCESS_KEY_ID'),
        'secret_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'region': 'us-east-1',
        'bucket_name': 'carboniq-bucket',
        'file_key': 'carboniq-cur/carboniq-cur/data/BILLING_PERIOD=2026-10/carboniq-cur-00001.csv.zip'
    },
    timeout=300
)

print(f'\nStatus Code: {response.status_code}')

if response.status_code == 200:
    data = response.json()
    
    if data.get('success'):
        print('\n✅ SUCCESS! AWS CUR data fetched and analyzed!\n')
        
        summary = data.get('summary', {})
        print(f'📊 Summary:')
        print(f'  Total Emissions: {summary.get("total_emissions_kg", 0):.2f} kg CO2e')
        print(f'  Total Cost: ${summary.get("total_cost", 0):.2f}')
        print(f'  Total Energy: {summary.get("total_energy_kwh", 0):.2f} kWh')
        print(f'  Top Service: {summary.get("top_service", "N/A")}')
        print(f'  Top Region: {summary.get("top_region", "N/A")}')
        
        analytics = data.get('analytics', {})
        
        # Show service breakdown
        if 'service_breakdown' in analytics:
            print(f'\n🔧 Service Breakdown:')
            for i, svc in enumerate(analytics['service_breakdown'][:5], 1):
                emissions = svc.get('emissions_kg', 0)
                cost = svc.get('cost', 0)
                energy = svc.get('energy_kwh', 0)
                print(f'  {i}. {svc.get("service", "N/A")}:')
                print(f'     Emissions: {emissions:.2f} kg CO2e | Energy: {energy:.2f} kWh | Cost: ${cost:.2f}')
        
        # Show regional breakdown
        if 'region_breakdown' in analytics:
            print(f'\n🌍 Regional Breakdown:')
            for i, reg in enumerate(analytics['region_breakdown'][:5], 1):
                emissions = reg.get('emissions_kg', 0)
                zone = reg.get('zone', 'N/A')
                intensity = reg.get('avg_carbon_intensity', 0)
                print(f'  {i}. {reg.get("region", "N/A")} ({zone}):')
                print(f'     Emissions: {emissions:.2f} kg CO2e | Intensity: {intensity:.0f} gCO2/kWh')
        
        # Show recommendations
        if 'recommendations' in data:
            recs = data['recommendations'].get('recommendations', [])
            if recs:
                print(f'\n💡 Recommendations ({len(recs)} found):')
                for i, rec in enumerate(recs[:3], 1):
                    print(f'  {i}. {rec.get("title", "N/A")}')
                    desc = rec.get("description", "")
                    if len(desc) > 100:
                        desc = desc[:100] + "..."
                    print(f'     {desc}')
                    savings = rec.get('estimated_savings', {})
                    if savings and 'emissions_kg' in savings:
                        print(f'     💰 Potential: {savings.get("emissions_kg", 0):.2f} kg CO2e savings')
        
        print(f'\n⏱️  Pipeline Duration: {data.get("duration", "N/A")}s')
    else:
        error = data.get('error', 'Unknown error')
        print(f'\n❌ Analysis failed: {error}')
else:
    print(f'\n❌ Request failed')
    print(f'Response: {response.text[:500]}')
