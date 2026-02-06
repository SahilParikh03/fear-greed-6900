"""
Market scoring functions for Fear & Greed Index.

This module provides scoring functions to convert raw market data into
normalized fear/greed scores based on various metrics like dominance and volatility.
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class DominanceScorer:
    """
    Score market sentiment based on Bitcoin dominance.

    Logic:
    - BTC Dominance > 55%: Fear/Safety (people moving to BTC as safe haven)
    - BTC Dominance < 45%: Greed/Speculation (people moving to altcoins)
    - 45-55%: Neutral zone (balanced market)

    Returns a score from 0 (Extreme Fear) to 100 (Extreme Greed).
    """

    def __init__(
        self,
        fear_threshold: float = 55.0,
        greed_threshold: float = 45.0
    ):
        """
        Initialize the dominance scorer.

        Args:
            fear_threshold: BTC dominance % above which indicates fear
            greed_threshold: BTC dominance % below which indicates greed
        """
        self.fear_threshold = fear_threshold
        self.greed_threshold = greed_threshold
        logger.info(
            f"DominanceScorer initialized: Fear>{fear_threshold}%, "
            f"Greed<{greed_threshold}%"
        )

    def score(self, btc_dominance: float) -> Dict[str, any]:
        """
        Calculate fear/greed score based on BTC dominance.

        Args:
            btc_dominance: Bitcoin dominance percentage (0-100)

        Returns:
            Dictionary containing:
                - score: Normalized score 0-100
                - signal: 'fear', 'neutral', or 'greed'
                - dominance: The input dominance value
                - reasoning: Explanation of the score
        """
        if btc_dominance > self.fear_threshold:
            # High dominance = Fear (flight to safety)
            # Map 55-100 -> score 0-35 (Fear zone)
            score = max(0, 35 - ((btc_dominance - self.fear_threshold) / 45 * 35))
            signal = "fear"
            reasoning = f"High BTC dominance ({btc_dominance:.2f}%) indicates flight to safety"

        elif btc_dominance < self.greed_threshold:
            # Low dominance = Greed (speculation in altcoins)
            # Map 0-45 -> score 65-100 (Greed zone)
            score = min(100, 65 + ((self.greed_threshold - btc_dominance) / 45 * 35))
            signal = "greed"
            reasoning = f"Low BTC dominance ({btc_dominance:.2f}%) indicates altcoin speculation"

        else:
            # Neutral zone (45-55%)
            # Map 45-55 -> score 35-65 (linear)
            score = 35 + ((btc_dominance - self.greed_threshold) /
                         (self.fear_threshold - self.greed_threshold) * 30)
            signal = "neutral"
            reasoning = f"BTC dominance ({btc_dominance:.2f}%) in neutral range"

        logger.debug(
            f"Dominance Score: {score:.2f} ({signal}) - Dominance: {btc_dominance:.2f}%"
        )

        return {
            "score": round(score, 2),
            "signal": signal,
            "dominance": btc_dominance,
            "reasoning": reasoning
        }


class VolatilityScorer:
    """
    Score market sentiment based on market cap volatility.

    Logic:
    - Market cap drops > 5%: Extreme Fear (panic selling)
    - Market cap gains > 5%: Extreme Greed (FOMO buying)
    - Small changes: Neutral

    Returns a score from 0 (Extreme Fear) to 100 (Extreme Greed).
    """

    def __init__(
        self,
        extreme_fear_threshold: float = -5.0,
        extreme_greed_threshold: float = 5.0
    ):
        """
        Initialize the volatility scorer.

        Args:
            extreme_fear_threshold: % drop that indicates extreme fear
            extreme_greed_threshold: % gain that indicates extreme greed
        """
        self.extreme_fear_threshold = extreme_fear_threshold
        self.extreme_greed_threshold = extreme_greed_threshold
        logger.info(
            f"VolatilityScorer initialized: Extreme Fear<{extreme_fear_threshold}%, "
            f"Extreme Greed>{extreme_greed_threshold}%"
        )

    def score(self, percentage_change: float) -> Dict[str, any]:
        """
        Calculate fear/greed score based on market cap volatility.

        Args:
            percentage_change: 24h percentage change in total market cap

        Returns:
            Dictionary containing:
                - score: Normalized score 0-100
                - signal: 'extreme_fear', 'fear', 'neutral', 'greed', or 'extreme_greed'
                - change: The input percentage change
                - reasoning: Explanation of the score
        """
        if percentage_change <= self.extreme_fear_threshold:
            # Extreme negative change = Extreme Fear
            # Map -5% to -∞ -> score 0-10
            score = max(0, 10 + (percentage_change - self.extreme_fear_threshold) * 2)
            signal = "extreme_fear"
            reasoning = f"Large market cap drop ({percentage_change:.2f}%) indicates panic selling"

        elif percentage_change < 0:
            # Moderate negative change = Fear
            # Map -5% to 0% -> score 10-45
            score = 10 + ((percentage_change / self.extreme_fear_threshold) * 35)
            signal = "fear"
            reasoning = f"Market cap declining ({percentage_change:.2f}%) indicates selling pressure"

        elif percentage_change < self.extreme_greed_threshold:
            # Moderate positive change = Greed
            # Map 0% to +5% -> score 55-90
            score = 55 + ((percentage_change / self.extreme_greed_threshold) * 35)
            signal = "greed"
            reasoning = f"Market cap growing ({percentage_change:.2f}%) indicates buying pressure"

        else:
            # Extreme positive change = Extreme Greed
            # Map +5% to +∞ -> score 90-100
            score = min(100, 90 + (percentage_change - self.extreme_greed_threshold) * 2)
            signal = "extreme_greed"
            reasoning = f"Large market cap surge ({percentage_change:.2f}%) indicates FOMO buying"

        logger.debug(
            f"Volatility Score: {score:.2f} ({signal}) - Change: {percentage_change:.2f}%"
        )

        return {
            "score": round(score, 2),
            "signal": signal,
            "change": percentage_change,
            "reasoning": reasoning
        }


def calculate_market_scores(
    btc_dominance: Optional[float] = None,
    market_cap_change: Optional[float] = None
) -> Dict[str, any]:
    """
    Calculate all market sentiment scores.

    Convenience function to calculate dominance and volatility scores in one call.

    Args:
        btc_dominance: Bitcoin dominance percentage
        market_cap_change: 24h percentage change in total market cap

    Returns:
        Dictionary containing dominance_score and volatility_score results
    """
    results = {}

    if btc_dominance is not None:
        dominance_scorer = DominanceScorer()
        results["dominance"] = dominance_scorer.score(btc_dominance)

    if market_cap_change is not None:
        volatility_scorer = VolatilityScorer()
        results["volatility"] = volatility_scorer.score(market_cap_change)

    logger.info(f"Calculated {len(results)} market scores")
    return results
