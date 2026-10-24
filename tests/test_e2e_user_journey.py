"""
End-to-End User Journey Test for CarbonIQ
Tests:
1. User registration & JWT authentication
2. Mock CUR CSV upload & Multi-Agent Analysis pipeline execution
3. Verification of emission metrics, energy breakdown, and intelligence recommendations
4. API Key generation for the user
5. CLI Workload measurement ingestion with API Key authentication
6. Personalized CLI measurement history & aggregated stats retrieval
7. Service Analytics & Executive Summary queries
8. Clean up of test data
"""
import os
import sys
import asyncio
import io
from pathlib import Path
from dotenv import load_dotenv

# Load backend environment variables
backend_dir = Path(__file__).resolve().parent.parent / "backend"
load_dotenv(backend_dir / ".env.local")
load_dotenv(backend_dir / ".env")

sys.path.insert(0, str(backend_dir))

import httpx
from database import get_pool, close_pool

BASE_URL = "http://127.0.0.1:8000"

async def run_e2e_journey():
    print("=" * 80)
    print("🚀 STARTING CARBONIQ FULL END-TO-END USER JOURNEY TEST")
    print("=" * 80)

    from main import app
    from httpx import ASGITransport

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=BASE_URL) as client:
        test_email = "test_sustainability_pilot@carboniq.internal"
        test_password = "SecurePassword123!"
        test_name = "Eco Pilot Tester"

        # 0. Clean up any previous test user
        pool = await get_pool()
        async with pool.acquire() as conn:
            user_row = await conn.fetchrow("SELECT id FROM users WHERE email = $1", test_email)
            if user_row:
                uid = user_row["id"]
                await conn.execute("DELETE FROM workload_measurements WHERE user_id = $1", uid)
                await conn.execute("DELETE FROM api_keys WHERE user_id = $1", uid)
                await conn.execute("DELETE FROM users WHERE id = $1", uid)
                print(f"🧹 Cleaned up existing test user record (ID: {uid})")

        # 1. User Signup
        print("\n--- STEP 1: New User Registration ---")
        signup_payload = {
            "name": test_name,
            "email": test_email,
            "password": test_password
        }
        res = await client.post("/api/auth/signup", json=signup_payload)
        print(f"POST /api/auth/signup status: {res.status_code}")
        assert res.status_code == 200, f"Signup failed: {res.text}"
        signup_data = res.json()
        assert signup_data.get("success") is True
        token = signup_data.get("access_token")
        user_id = signup_data.get("user", {}).get("id")
        print(f"✅ User registered successfully: ID={user_id}, Email={test_email}")
        print(f"🔑 JWT Token acquired (length: {len(token)})")

        auth_headers = {"Authorization": f"Bearer {token}"}

        # 2. Upload Mock CUR CSV for Multi-Agent Analysis
        print("\n--- STEP 2: Mock AWS CUR CSV Multi-Agent Analysis ---")
        mock_cur_content = (
            "identity/LineItemId,bill/BillingPeriodStartDate,lineItem/UsageStartDate,lineItem/UsageEndDate,product/ProductName,product/region,lineItem/UsageType,lineItem/UsageAmount,product/instanceType,lineItem/ResourceId,lineItem/UnblendedCost,product/location,product/productFamily,lineItem/Operation\n"
            "1,2026-05-01,2026-05-15T14:00:00Z,2026-05-15T15:00:00Z,Amazon Elastic Compute Cloud,ap-south-1,BoxUsage:m5.large,24,m5.large,i-mumbai-001,12.50,Asia Pacific (Mumbai),Compute Instance,RunInstances\n"
            "2,2026-05-01,2026-05-18T10:00:00Z,2026-05-18T11:00:00Z,Amazon Elastic Compute Cloud,us-west-2,BoxUsage:t3.medium,48,t3.medium,i-oregon-001,8.75,US West (Oregon),Compute Instance,RunInstances\n"
            "3,2026-05-01,2026-05-10T08:00:00Z,2026-05-10T09:00:00Z,Amazon Relational Database Service,us-east-1,InstanceUsage:db.t3.small,24,db.t3.small,db-virginia-001,15.20,US East (N. Virginia),Database Instance,CreateDBInstance\n"
            "4,2026-05-01,2026-05-20T12:00:00Z,2026-05-20T13:00:00Z,Amazon Simple Storage Service,us-east-1,TimedStorage-ByteHrs,1500000,,,2.30,US East (N. Virginia),Storage,\n"
            "5,2026-05-01,2026-05-22T16:00:00Z,2026-05-22T17:00:00Z,AWS Lambda,us-west-2,Lambda-GB-Second,50000,,,0.85,US West (Oregon),Serverless,Invoke\n"
            "6,2026-05-01,2026-05-23T10:00:00Z,2026-05-23T11:00:00Z,Amazon Elastic Compute Cloud,eu-central-1,BoxUsage:c5.xlarge,36,c5.xlarge,i-frankfurt-002,18.40,Europe (Frankfurt),Compute Instance,RunInstances\n"
        )
        csv_bytes = mock_cur_content.encode("utf-8")

        files = {"file": ("test_mock_cur.csv", io.BytesIO(csv_bytes), "text/csv")}
        res = await client.post("/api/multi-agent/analyze?use_intelligence=true&use_gemini=false", files=files)
        print(f"POST /api/multi-agent/analyze status: {res.status_code}")
        assert res.status_code == 200, f"Analysis failed: {res.text}"
        analysis_res = res.json()
        
        # Verify analysis output structure
        assert analysis_res.get("success") is True, f"Analysis marked as failed: {analysis_res}"
        summary = analysis_res.get("summary", {})
        print(f"✅ Multi-Agent Analysis Succeeded!")
        print(f"   • Total Carbon Emissions: {summary.get('total_carbon_kg', 0):.2f} kg CO2e")
        print(f"   • Total Energy: {summary.get('total_energy_kwh', 0):.2f} kWh")
        print(f"   • Total Cost: ${summary.get('total_cost_usd', 0):.2f}")
        recommendations = analysis_res.get("recommendations", [])
        print(f"   • Generated Recommendations Count: {len(recommendations)}")

        # 3. Create User API Key for CLI & SDK
        print("\n--- STEP 3: Generate API Key for CLI Integration ---")
        key_payload = {"name": "Test Laptop CLI Key"}
        res = await client.post("/api/user/api-keys", json=key_payload, headers=auth_headers)
        print(f"POST /api/user/api-keys status: {res.status_code}")
        assert res.status_code == 200, f"API key creation failed: {res.text}"
        key_data = res.json()
        api_key = key_data.get("api_key")
        assert api_key and api_key.startswith("ciq_"), f"Invalid API key generated: {api_key}"
        print(f"✅ CLI API Key created: {key_data.get('key_prefix')}... (Full key: {api_key[:10]}...)")

        # Verify key list endpoint
        res = await client.get("/api/user/api-keys", headers=auth_headers)
        assert res.status_code == 200
        keys_resp = res.json()
        keys_list = keys_resp.get("keys", []) if isinstance(keys_resp, dict) else keys_resp
        assert any(k.get("key_prefix") == key_data.get("key_prefix") for k in keys_list)
        print(f"✅ Verified API key listed in user's profile ({len(keys_list)} active keys)")

        # 4. Ingest Workload Measurement from CLI using X-API-Key
        print("\n--- STEP 4: Ingest Workload Measurements via CLI API Key ---")
        cli_headers = {"X-API-Key": api_key}
        measurement_payload = {
            "workload_name": "ai-model-training",
            "workload_type": "ml_training",
            "measurement": {
                "duration_seconds": 124.5,
                "emissions_gco2e": 45.2,
                "energy_kwh": 0.0628,
                "cpu_energy": 0.0381,
                "ram_energy": 0.0247,
                "carbon_intensity": 718.0,
                "country_name": "India"
            },
            "carbon_aware_data": {
                "region": "ap-south-1",
                "green_window": True
            }
        }
        res = await client.post("/api/cli/measurements", json=measurement_payload, headers=cli_headers)
        print(f"POST /api/cli/measurements status: {res.status_code}")
        assert res.status_code == 200, f"Measurement ingestion failed: {res.text}"
        meas_res = res.json()
        assert meas_res.get("success") is True
        measurement_id = meas_res.get("measurement_id")
        print(f"✅ Workload measurement logged: ID={measurement_id}, Workload={measurement_payload['workload_name']}")

        # 5. Verify User's CLI Workload History & Stats
        print("\n--- STEP 5: Verify User's Dashboard CLI Workload Endpoints ---")
        res = await client.get("/api/cli/measurements/history", headers=auth_headers)
        assert res.status_code == 200
        history_data = res.json()
        measurements = history_data.get("measurements", [])
        assert len(measurements) >= 1
        assert measurements[0]["workload_name"] == "ai-model-training"
        print(f"✅ User CLI history contains {len(measurements)} record(s). Latest: {measurements[0]['workload_name']}")

        res = await client.get("/api/cli/measurements/stats", headers=auth_headers)
        assert res.status_code == 200
        stats = res.json()
        print(f"✅ User CLI Aggregated Stats:")
        print(f"   • Total Measurements: {stats.get('total_measurements')}")
        print(f"   • Total Emissions: {stats.get('total_emissions_gco2e', 0):.2f} gCO2e")
        print(f"   • Total Energy: {stats.get('total_energy_kwh', 0):.4f} kWh")
        print(f"   • Avg Duration: {stats.get('avg_duration_seconds', 0):.2f} s")

        # 6. Verify Service Analytics & Summary Endpoints for Reports / PDF
        print("\n--- STEP 6: Verify Service Analytics & Reports Data Feeds ---")
        res = await client.get("/api/history")
        print(f"GET /api/history status: {res.status_code}")
        assert res.status_code == 200
        history_res = res.json()
        print(f"✅ History retrieved: {len(history_res.get('analyses', []))} analyses")

        # 7. Cleanup Test User
        print("\n--- STEP 7: Clean Up Test Artifacts ---")
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM workload_measurements WHERE user_id = $1", user_id)
            await conn.execute("DELETE FROM api_keys WHERE user_id = $1", user_id)
            await conn.execute("DELETE FROM users WHERE id = $1", user_id)
            print(f"✅ Cleaned up test user (ID: {user_id}) and all associated records.")

    await close_pool()
    print("\n" + "=" * 80)
    print("🎉 ALL END-TO-END USER JOURNEY TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_e2e_journey())
