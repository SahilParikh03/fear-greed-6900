"""
Fear & Greed Index 6900 - Dashboard

This script displays the complete Master Index with all component scores
and historical comparison in a clean terminal dashboard.
"""

import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

from src.fetchers import CMCFetcher
from src.normalizers.market_scorers import VolatilityScorer, DominanceScorer
from src.normalizers.social_scorer import SocialSentimentScorer
from src.aggregator.brain import MasterAggregator
from src.utils.history_manager import HistoryManager

# Setup logging
logging.basicConfig(
    level=logging.WARNING,  # Quiet for clean dashboard output
    format='%(levelname)s: %(message)s'
)

logger = logging.getLogger(__name__)


def print_header():
    """Print the dashboard header."""
    print("\n" + "=" * 70)
    print("  FEAR & GREED INDEX 6900 - Master Dashboard".center(70))
    print("=" * 70)
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(70))
    print("=" * 70 + "\n")


def print_section_header(title: str):
    """Print a section header."""
    print(f"\n{title}")
    print("-" * 70)


def print_component_scores(volatility_result: dict, dominance_result: dict, social_result: dict):
    """Print individual component scores in a table."""
    print_section_header("COMPONENT SCORES")

    # Table header
    print(f"{'Component':<20} {'Score':<10} {'Signal':<18} {'Details':<22}")
    print("-" * 70)

    # Volatility row
    vol_score = volatility_result['score']
    vol_signal = volatility_result['signal'].upper().replace('_', ' ')
    vol_change = volatility_result['change']
    print(
        f"{'Volatility (40%)':<20} "
        f"{vol_score:<10.2f} "
        f"{vol_signal:<18} "
        f"24h Change: {vol_change:>6.2f}%"
    )

    # Dominance row
    dom_score = dominance_result['score']
    dom_signal = dominance_result['signal'].upper()
    dom_value = dominance_result['dominance']
    print(
        f"{'Dominance (30%)':<20} "
        f"{dom_score:<10.2f} "
        f"{dom_signal:<18} "
        f"BTC Dom: {dom_value:>8.2f}%"
    )

    # Social row
    social_score = social_result['score']
    social_signal = social_result['signal'].upper()
    social_source = f"({social_result['source']})"
    print(
        f"{'Social (30%)':<20} "
        f"{social_score:<10.2f} "
        f"{social_signal:<18} "
        f"Source: {social_source:>10}"
    )

    print("-" * 70)


def print_master_index(master_result: dict):
    """Print the master index score with dramatic styling."""
    print_section_header("MASTER INDEX")

    score = master_result['score']
    label = master_result['label']

    # Create a visual bar (ASCII-safe for Windows)
    bar_length = 50
    filled = int((score / 100) * bar_length)
    bar = "#" * filled + "-" * (bar_length - filled)

    # Color-code the output (using just text for now)
    print(f"\n  [{bar}]")
    print(f"\n  Score: {score:.2f} / 100")
    print(f"  Status: {label}")
    print(f"\n  {'0 (FEAR)':<25} {'50 (NEUTRAL)':^25} {'100 (GREED)':>20}")
    print("-" * 70)


def print_change_from_yesterday(current_score: float, history_manager: HistoryManager):
    """Print comparison to yesterday's index value."""
    print_section_header("CHANGE FROM YESTERDAY")

    # Get historical data (last 2 records to compare)
    history = history_manager.load_history(limit=2)

    if len(history) < 2:
        print("  Insufficient historical data for comparison")
        print("  (Need at least 2 snapshots)")
    else:
        # For now, we'll use market cap change as a proxy
        # In a real implementation, we'd store the actual index scores
        prev_market_cap = history[1]['total_market_cap']
        curr_market_cap = history[0]['total_market_cap']
        market_cap_change = ((curr_market_cap - prev_market_cap) / prev_market_cap) * 100

        prev_btc_dom = history[1]['btc_dominance']
        curr_btc_dom = history[0]['btc_dominance']
        dom_change = curr_btc_dom - prev_btc_dom

        print(f"  Market Cap Change:     {market_cap_change:>+8.2f}%")
        print(f"  BTC Dominance Change:  {dom_change:>+8.2f}%")
        print(f"\n  Previous Market Cap:   ${prev_market_cap:>17,.0f}")
        print(f"  Current Market Cap:    ${curr_market_cap:>17,.0f}")

    print("-" * 70)


def print_market_overview(global_data: dict):
    """Print general market overview."""
    print_section_header("MARKET OVERVIEW")

    data = global_data['data']
    quote = data['quote']['USD']

    total_market_cap = quote['total_market_cap']
    total_volume = quote['total_volume_24h']
    btc_dominance = data['btc_dominance']
    active_cryptos = data['active_cryptocurrencies']
    market_cap_change = quote.get('total_market_cap_yesterday_percentage_change', 0)

    print(f"  Total Market Cap:      ${total_market_cap:>17,.0f}")
    print(f"  24h Volume:            ${total_volume:>17,.0f}")
    print(f"  BTC Dominance:         {btc_dominance:>17.2f}%")
    print(f"  Active Cryptocurrencies: {active_cryptos:>15,}")
    print(f"  24h Change:            {market_cap_change:>+17.2f}%")
    print("-" * 70)


def print_footer():
    """Print dashboard footer."""
    print("\n" + "=" * 70)
    print("  Powered by CoinMarketCap API".center(70))
    print("  Custom Index by Fear & Greed 6900 System".center(70))
    print("=" * 70 + "\n")


async def main():
    """Main dashboard function."""
    # Load environment
    dotenv_path = find_dotenv(usecwd=True)
    if dotenv_path:
        load_dotenv(dotenv_path)

    # Initialize components
    history_manager = HistoryManager()
    volatility_scorer = VolatilityScorer()
    dominance_scorer = DominanceScorer()
    social_scorer = SocialSentimentScorer()
    aggregator = MasterAggregator()

    try:
        # Fetch market data
        async with CMCFetcher() as fetcher:
            # Health check
            if not await fetcher.health_check():
                print("ERROR: CoinMarketCap API is not responding!")
                return

            # Fetch global metrics
            global_data = await fetcher.fetch_global_metrics()
            data = global_data['data']
            quote = data['quote']['USD']

            # Extract metrics
            btc_dominance = data['btc_dominance']
            total_market_cap = quote['total_market_cap']
            total_volume = quote['total_volume_24h']
            market_cap_change_24h = quote.get('total_market_cap_yesterday_percentage_change', 0)

            # Save snapshot to history
            history_manager.save_snapshot(
                total_market_cap=total_market_cap,
                btc_dominance=btc_dominance,
                total_volume_24h=total_volume,
                market_cap_change_24h=market_cap_change_24h
            )

        # Calculate component scores
        volatility_result = volatility_scorer.score(market_cap_change_24h)
        dominance_result = dominance_scorer.score(btc_dominance)
        social_result = social_scorer.get_combined_social_score()

        # Calculate master index
        master_result = aggregator.calculate_master_score(
            volatility_score=volatility_result['score'],
            dominance_score=dominance_result['score'],
            social_score=social_result['score']
        )

        # Display dashboard
        print_header()
        print_master_index(master_result)
        print_component_scores(volatility_result, dominance_result, social_result)
        print_change_from_yesterday(master_result['score'], history_manager)
        print_market_overview(global_data)
        print_footer()

        # Print interpretation
        interpretation = aggregator.get_detailed_interpretation(master_result['score'])
        print(f"[i] Interpretation:")
        print(f"   {interpretation}\n")

    except Exception as e:
        logger.error(f"Dashboard error: {e}", exc_info=True)
        print(f"\n[!] ERROR: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
