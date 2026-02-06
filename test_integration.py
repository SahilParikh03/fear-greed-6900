"""
Integration test for CMC fetcher, market scorers, and history manager.

This script tests the complete data pipeline:
1. Fetch data from CoinMarketCap API
2. Extract market metrics
3. Calculate fear/greed scores
4. Save to history
"""

import asyncio
import json
import logging
from pathlib import Path

from src.fetchers.cmc_fetcher import CMCFetcher
from src.normalizers.market_scorers import calculate_market_scores
from src.utils.history_manager import HistoryManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Run the integration test."""
    print("\n" + "="*80)
    print("FEAR & GREED INDEX 6900 - Integration Test")
    print("="*80 + "\n")

    # Initialize history manager
    history_manager = HistoryManager()
    logger.info("History manager initialized")

    # Fetch data from CoinMarketCap
    async with CMCFetcher() as fetcher:
        logger.info("Fetching data from CoinMarketCap...")
        data = await fetcher.fetch()

        # Extract global metrics
        global_data = data.get("global_metrics", {}).get("data", {})

        if not global_data:
            logger.error("No global metrics data received!")
            return

        # Extract key metrics
        quote = global_data.get("quote", {}).get("USD", {})

        total_market_cap = quote.get("total_market_cap", 0)
        btc_dominance = global_data.get("btc_dominance", 0)
        total_volume_24h = quote.get("total_volume_24h", 0)
        market_cap_change_24h = quote.get("total_market_cap_yesterday_percentage_change", 0)

        print("\n" + "-"*80)
        print("CURRENT MARKET METRICS")
        print("-"*80)
        print(f"Total Market Cap:     ${total_market_cap:,.2f}")
        print(f"BTC Dominance:        {btc_dominance:.2f}%")
        print(f"24h Volume:           ${total_volume_24h:,.2f}")
        print(f"24h Market Cap Change: {market_cap_change_24h:+.2f}%")
        print("-"*80 + "\n")

        # Calculate fear/greed scores
        logger.info("Calculating market sentiment scores...")
        scores = calculate_market_scores(
            btc_dominance=btc_dominance,
            market_cap_change=market_cap_change_24h
        )

        print("-"*80)
        print("FEAR & GREED SCORES")
        print("-"*80)

        if "dominance" in scores:
            dom = scores["dominance"]
            print(f"\nDominance Score: {dom['score']}/100 ({dom['signal'].upper()})")
            print(f"  >> {dom['reasoning']}")

        if "volatility" in scores:
            vol = scores["volatility"]
            print(f"\nVolatility Score: {vol['score']}/100 ({vol['signal'].upper()})")
            print(f"  >> {vol['reasoning']}")

        print("-"*80 + "\n")

        # Save to history
        logger.info("Saving data to history...")
        success = history_manager.save_snapshot(
            total_market_cap=total_market_cap,
            btc_dominance=btc_dominance,
            total_volume_24h=total_volume_24h,
            market_cap_change_24h=market_cap_change_24h
        )

        if not success:
            logger.error("Failed to save data to history!")
            return

        # Display history stats
        stats = history_manager.get_stats()
        print("-"*80)
        print("HISTORY STATS")
        print("-"*80)
        print(f"Total Records:   {stats.get('record_count', 0)}")
        if stats.get('newest_record'):
            print(f"Latest Snapshot: {stats.get('newest_record')}")
        if stats.get('oldest_record'):
            print(f"Oldest Snapshot: {stats.get('oldest_record')}")
        print(f"File Path:       {stats.get('file_path', 'N/A')}")
        print("-"*80 + "\n")

        # Save full raw data for inspection
        output_file = Path("data/processed/latest_fetch.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

        print(f"[OK] Full API response saved to: {output_file}\n")

    print("="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
