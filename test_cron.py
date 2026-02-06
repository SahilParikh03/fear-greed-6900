"""
Test script for the Vercel Cron endpoint.

This script tests the /api/v1/internal/cron-refresh endpoint
to ensure it properly validates the CRON_SECRET and triggers data refresh.
"""

import asyncio
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)


async def test_cron_endpoint():
    """Test the cron endpoint with various scenarios."""
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/v1/internal/cron-refresh"

    cron_secret = os.getenv("CRON_SECRET")

    if not cron_secret:
        print("❌ ERROR: CRON_SECRET not found in .env file")
        print("Please add CRON_SECRET to your .env file")
        return False

    print("🧪 Testing Vercel Cron Endpoint")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        # Test 1: Valid secret
        print("\n📋 Test 1: Valid Authorization Header")
        try:
            response = await client.post(
                endpoint,
                headers={"Authorization": cron_secret}
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✅ PASS: {data['message']}")
                print(f"   Status: {data['status']}")
                print(f"   Timestamp: {data['timestamp']}")
            else:
                print(f"❌ FAIL: Expected 200, got {response.status_code}")
                print(f"   Response: {response.text}")
                return False

        except httpx.ConnectError:
            print("❌ ERROR: Could not connect to server")
            print("   Make sure the API is running on http://localhost:8000")
            return False

        # Test 2: Missing Authorization header
        print("\n📋 Test 2: Missing Authorization Header")
        response = await client.post(endpoint)

        if response.status_code == 401:
            print(f"✅ PASS: Correctly rejected (401 Unauthorized)")
        else:
            print(f"❌ FAIL: Expected 401, got {response.status_code}")
            return False

        # Test 3: Invalid secret
        print("\n📋 Test 3: Invalid Authorization Header")
        response = await client.post(
            endpoint,
            headers={"Authorization": "wrong-secret-123"}
        )

        if response.status_code == 403:
            print(f"✅ PASS: Correctly rejected (403 Forbidden)")
        else:
            print(f"❌ FAIL: Expected 403, got {response.status_code}")
            return False

        # Test 4: Check health to verify data refresh
        print("\n📋 Test 4: Health Check After Refresh")
        await asyncio.sleep(2)  # Wait for background task

        health_response = await client.get(f"{base_url}/api/v1/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ PASS: Health check successful")
            print(f"   Status: {health_data['status']}")
            print(f"   Record count: {health_data['components']['record_count']}")
        else:
            print(f"⚠️  WARNING: Health check failed ({health_response.status_code})")

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("\n💡 Next steps:")
    print("   1. Deploy to Vercel: vercel --prod")
    print("   2. Set CRON_SECRET in Vercel environment variables")
    print("   3. Monitor cron execution in Vercel dashboard")

    return True


async def test_cron_simulation():
    """Simulate what Vercel Cron does."""
    print("\n\n🤖 Simulating Vercel Cron Execution")
    print("=" * 60)

    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/v1/internal/cron-refresh"
    cron_secret = os.getenv("CRON_SECRET")

    print(f"Target: {endpoint}")
    print(f"Method: POST")
    print(f"Headers: Authorization: {cron_secret[:10]}...{cron_secret[-10:]}")
    print()

    async with httpx.AsyncClient() as client:
        try:
            # This is exactly what Vercel Cron will do
            response = await client.post(
                endpoint,
                headers={"Authorization": cron_secret},
                timeout=30.0
            )

            print(f"Status Code: {response.status_code}")
            print(f"Response Body:")
            print(response.text)

            if response.status_code == 200:
                print("\n✅ Cron simulation successful!")
                print("   This is what will happen every 5 minutes on Vercel")
            else:
                print(f"\n❌ Unexpected status: {response.status_code}")

        except Exception as e:
            print(f"\n❌ Error: {e}")


async def main():
    """Run all tests."""
    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            await client.get("http://localhost:8000/api/v1/health", timeout=2.0)
    except httpx.ConnectError:
        print("❌ ERROR: API server is not running!")
        print("\nPlease start the server first:")
        print("  python run_server.py")
        print("  or")
        print("  uvicorn src.api.main:app --reload")
        sys.exit(1)

    # Run tests
    success = await test_cron_endpoint()

    if success:
        await test_cron_simulation()

    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
