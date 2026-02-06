"""
Example script demonstrating how to use the CMCFetcher.

This script shows how to:
1. Initialize the fetcher
2. Fetch global metrics
3. Fetch cryptocurrency quotes
4. Use the combined fetch method
5. Perform health checks
"""

import asyncio
import json
import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

from src.fetchers import CMCFetcher


async def main():
    """Main example function."""
    # Debug: Show where we're running from
    print("=" * 60)
    print("Environment Debug Information")
    print("=" * 60)
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {Path(__file__).parent.absolute()}")

    # Try to find .env file
    dotenv_path = find_dotenv(usecwd=True)
    if dotenv_path:
        print(f".env file found at: {dotenv_path}")
        load_dotenv(dotenv_path)
    else:
        print("No .env file found - will rely on system environment variables")

    # Check if API key is available before initializing fetcher
    api_key_found = os.getenv("CMC_API_KEY") is not None
    print(f"CMC_API_KEY environment variable: {'Found' if api_key_found else 'NOT FOUND'}")
    print("=" * 60)

    # Initialize the fetcher (will use CMC_API_KEY from .env)
    async with CMCFetcher() as fetcher:
        print("=" * 60)
        print("CMC Fetcher Example")
        print("=" * 60)

        # 1. Health check
        print("\n1. Performing health check...")
        is_healthy = await fetcher.health_check()
        print(f"   API is {'healthy' if is_healthy else 'unhealthy'}")

        if not is_healthy:
            print("   Exiting due to unhealthy API")
            return

        # 2. Fetch global metrics
        print("\n2. Fetching global market metrics...")
        try:
            global_data = await fetcher.fetch_global_metrics()
            btc_dominance = global_data["data"]["btc_dominance"]
            total_market_cap = global_data["data"]["quote"]["USD"]["total_market_cap"]
            total_volume = global_data["data"]["quote"]["USD"]["total_volume_24h"]

            print(f"   BTC Dominance: {btc_dominance:.2f}%")
            print(f"   Total Market Cap: ${total_market_cap:,.0f}")
            print(f"   24h Volume: ${total_volume:,.0f}")
        except Exception as e:
            print(f"   Error fetching global metrics: {e}")

        # 3. Fetch specific cryptocurrency quotes
        print("\n3. Fetching BTC quote...")
        try:
            btc_data = await fetcher.fetch_crypto_quotes(symbols=["BTC"])
            btc_quote = btc_data["data"]["BTC"][0]["quote"]["USD"]

            print(f"   BTC Price: ${btc_quote['price']:,.2f}")
            print(f"   24h Change: {btc_quote['percent_change_24h']:.2f}%")
            print(f"   24h Volume: ${btc_quote['volume_24h']:,.0f}")
        except Exception as e:
            print(f"   Error fetching BTC quote: {e}")

        # 4. Fetch top 10 cryptocurrencies
        print("\n4. Fetching top 10 cryptocurrencies...")
        try:
            top_coins = await fetcher.fetch_crypto_quotes(limit=10)
            print(f"   Retrieved data for {len(top_coins['data'])} coins")
        except Exception as e:
            print(f"   Error fetching top coins: {e}")

        # 5. Use the combined fetch method
        print("\n5. Fetching all data with combined method...")
        try:
            all_data = await fetcher.fetch()
            print(f"   Timestamp: {all_data['timestamp']}")
            print(f"   Global metrics fetched: {'global_metrics' in all_data}")
            print(f"   Crypto quotes fetched: {'crypto_quotes' in all_data}")

            # Display summary
            print("\n   Summary:")
            print(f"   - BTC Dominance: {all_data['global_metrics']['data']['btc_dominance']:.2f}%")
            print(f"   - Active Cryptocurrencies: {all_data['global_metrics']['data']['active_cryptocurrencies']:,}")
            print(f"   - Coins fetched: {len(all_data['crypto_quotes']['data'])}")

        except Exception as e:
            print(f"   Error fetching all data: {e}")

        print("\n" + "=" * 60)
        print(f"Raw data saved to: {fetcher.data_dir}")
        print("=" * 60)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
