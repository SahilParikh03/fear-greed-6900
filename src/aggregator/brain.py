"""
Master aggregator for the Fear & Greed Index 6900.

This module combines multiple sentiment signals (volatility, dominance, social)
into a single master score with interpretive labels.
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class MasterAggregator:
    """
    The "brain" that combines all sentiment signals into a single Fear & Greed Index.

    Weighting:
    - Volatility: 40% (market behavior is king)
    - Dominance: 30% (BTC safe haven vs altcoin speculation)
    - Social Sentiment: 30% (future: news/twitter sentiment)

    Score ranges:
    - 0-24: Extreme Fear
    - 25-44: Fear
    - 45-55: Neutral
    - 56-75: Greed
    - 76-100: Extreme Greed
    """

    def __init__(
        self,
        volatility_weight: float = 0.40,
        dominance_weight: float = 0.30,
        social_weight: float = 0.30
    ):
        """
        Initialize the Master Aggregator.

        Args:
            volatility_weight: Weight for volatility score (default 40%)
            dominance_weight: Weight for dominance score (default 30%)
            social_weight: Weight for social sentiment score (default 30%)
        """
        # Validate weights sum to 1.0
        total_weight = volatility_weight + dominance_weight + social_weight
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(
                f"Weights must sum to 1.0, got {total_weight:.2f}. "
                f"(volatility={volatility_weight}, dominance={dominance_weight}, "
                f"social={social_weight})"
            )

        self.volatility_weight = volatility_weight
        self.dominance_weight = dominance_weight
        self.social_weight = social_weight

        logger.info(
            f"MasterAggregator initialized - Weights: "
            f"Volatility={volatility_weight*100:.0f}%, "
            f"Dominance={dominance_weight*100:.0f}%, "
            f"Social={social_weight*100:.0f}%"
        )

    def calculate_master_score(
        self,
        volatility_score: Optional[float] = None,
        dominance_score: Optional[float] = None,
        social_score: Optional[float] = None
    ) -> Dict[str, any]:
        """
        Calculate the master Fear & Greed Index score.

        Args:
            volatility_score: Market cap volatility score (0-100)
            dominance_score: BTC dominance score (0-100)
            social_score: Social sentiment score (0-100)

        Returns:
            Dictionary containing:
                - score: The master index value (0-100)
                - label: Interpretive label for the score
                - components: Breakdown of individual scores
                - weights: The weights used for each component
        """
        components = {}
        weighted_sum = 0.0
        total_weight = 0.0

        # Add volatility component
        if volatility_score is not None:
            components["volatility"] = volatility_score
            weighted_sum += volatility_score * self.volatility_weight
            total_weight += self.volatility_weight
        else:
            logger.warning("Volatility score not provided")

        # Add dominance component
        if dominance_score is not None:
            components["dominance"] = dominance_score
            weighted_sum += dominance_score * self.dominance_weight
            total_weight += self.dominance_weight
        else:
            logger.warning("Dominance score not provided")

        # Add social component
        if social_score is not None:
            components["social"] = social_score
            weighted_sum += social_score * self.social_weight
            total_weight += self.social_weight
        else:
            logger.warning("Social score not provided")

        # Calculate final score (normalize if some components are missing)
        if total_weight > 0:
            master_score = weighted_sum / total_weight
        else:
            logger.error("No valid scores provided!")
            master_score = 50.0  # Default to neutral

        # Determine label based on score ranges
        label = self._get_label(master_score)

        logger.info(
            f"Master Score Calculated: {master_score:.2f} - {label} "
            f"(Components: {len(components)})"
        )

        return {
            "score": round(master_score, 2),
            "label": label,
            "components": components,
            "weights": {
                "volatility": self.volatility_weight,
                "dominance": self.dominance_weight,
                "social": self.social_weight
            }
        }

    def _get_label(self, score: float) -> str:
        """
        Get interpretive label for a given score.

        Args:
            score: Master score (0-100)

        Returns:
            Label string describing market sentiment
        """
        if score < 25:
            return "EXTREME FEAR"
        elif score < 45:
            return "FEAR"
        elif score <= 55:
            return "NEUTRAL"
        elif score <= 75:
            return "GREED"
        else:
            return "EXTREME GREED"

    def get_detailed_interpretation(self, score: float) -> str:
        """
        Get a detailed interpretation of what the score means.

        Args:
            score: Master score (0-100)

        Returns:
            Human-readable interpretation
        """
        if score < 25:
            return (
                "Market is in EXTREME FEAR. Investors are very worried. "
                "This could be a buying opportunity (be greedy when others are fearful)."
            )
        elif score < 45:
            return (
                "Market is in FEAR mode. Investors are concerned but not panicking. "
                "Caution is warranted, but opportunities may emerge."
            )
        elif score <= 55:
            return (
                "Market sentiment is NEUTRAL. No strong fear or greed signals. "
                "Balanced risk/reward environment."
            )
        elif score <= 75:
            return (
                "Market is in GREED mode. Investors are optimistic and buying. "
                "Be cautious of overvaluation and FOMO."
            )
        else:
            return (
                "Market is in EXTREME GREED. Investors are euphoric and complacent. "
                "High risk of correction (be fearful when others are greedy)."
            )
