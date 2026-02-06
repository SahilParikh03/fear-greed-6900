"""
Test script to verify the Fear & Greed Index API.

This script:
1. Refreshes data from CoinMarketCap
2. Retrieves the current index
3. Displays historical data

Run this after starting the server with: python run_server.py
"""

import asyncio
import httpx


async def test_api():
    """Test all API endpoints."""
    base_url = "http://127.0.0.1:8000"

    async with httpx.AsyncClient(timeout=30.0) as client:
        print("=" * 60)
        print("Testing Fear & Greed Index 6900 API")
        print("=" * 60)

        # Test 1: Root endpoint
        print("\n[1] Testing root endpoint...")
        response = await client.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        # Test 2: Health check
        print("\n[2] Testing health check...")
        response = await client.get(f"{base_url}/api/v1/health")
        print(f"Status: {response.status_code}")
        health = response.json()
        print(f"API Status: {health['status']}")
        print(f"Record Count: {health['components']['record_count']}")

        # Test 3: Refresh data (if no data exists)
        if health['components']['record_count'] == 0:
            print("\n[3] No data found. Refreshing from CoinMarketCap...")
            response = await client.post(f"{base_url}/api/v1/refresh")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            print("Waiting 5 seconds for background task to complete...")
            await asyncio.sleep(5)
        else:
            print(f"\n[3] Skipping refresh - {health['components']['record_count']} records exist")

        # Test 4: Get current index
        print("\n[4] Getting current Fear & Greed Index...")
        response = await client.get(f"{base_url}/api/v1/index")
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            index = response.json()
            print("\n" + "=" * 60)
            print("FEAR & GREED INDEX 6900")
            print("=" * 60)
            print(f"Master Score: {index['master_score']:.2f}")
            print(f"Sentiment:    {index['sentiment']}")
            print(f"Timestamp:    {index['timestamp']}")
            print("\nComponent Breakdown:")
            print(f"  • Volatility:  {index['breakdown']['volatility']:.2f}")
            print(f"  • Dominance:   {index['breakdown']['dominance']:.2f}")
            print(f"  • Social:      {index['breakdown']['social']:.2f}")
            print("\nWeights:")
            print(f"  • Volatility:  {index['weights']['volatility']*100:.0f}%")
            print(f"  • Dominance:   {index['weights']['dominance']*100:.0f}%")
            print(f"  • Social:      {index['weights']['social']*100:.0f}%")
            print("\nComponent Details:")
            for component, details in index['component_details'].items():
                print(f"\n  {component.upper()}:")
                print(f"    Score: {details['score']:.2f}")
                print(f"    Signal: {details['signal']}")
                print(f"    Reasoning: {details['reasoning']}")
            print("=" * 60)
        else:
            print(f"Error: {response.text}")

        # Test 5: Get history
        print("\n[5] Getting historical data (last 7 days)...")
        response = await client.get(f"{base_url}/api/v1/history?days=7")
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            history = response.json()
            print(f"\nFound {history['count']} historical records:")
            for i, record in enumerate(history['data'][:3], 1):  # Show first 3
                print(f"\n  Record {i}:")
                print(f"    Timestamp: {record['timestamp']}")
                print(f"    Market Cap: ${record['total_market_cap']:,.0f}")
                print(f"    BTC Dominance: {record['btc_dominance']:.2f}%")
                if record.get('market_cap_change_24h'):
                    print(f"    24h Change: {record['market_cap_change_24h']:.2f}%")
        else:
            print(f"Error: {response.text}")

        print("\n" + "=" * 60)
        print("API Test Complete!")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_api())
