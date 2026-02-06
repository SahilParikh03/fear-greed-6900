"""
Social sentiment scoring for Fear & Greed Index.

This module provides sentiment analysis based on news and social media.
Currently implements a mock scorer that can be manually configured for testing.

Future integrations:
- X (Twitter) sentiment API
- News sentiment API (CryptoPanic, NewsAPI, etc.)
- Reddit sentiment
- Google Trends
"""

import logging
from pathlib import Path
from typing import Dict, Optional
import json

logger = logging.getLogger(__name__)


class SocialSentimentScorer:
    """
    Score market sentiment based on social signals and news.

    Currently a "mock" implementation that returns a configurable score.
    This allows testing the full pipeline while social APIs are being integrated.

    Returns a score from 0 (Extreme Fear) to 100 (Extreme Greed).
    """

    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize the social sentiment scorer.

        Args:
            config_file: Path to JSON config file for overriding sentiment scores
        """
        self.config_file = config_file or Path("config/social_sentiment.json")
        self.default_score = 50.0  # Neutral by default

        logger.info(
            f"SocialSentimentScorer initialized (MOCK MODE) - "
            f"Default: {self.default_score}, Config: {self.config_file}"
        )

    def get_news_sentiment(self) -> Dict[str, any]:
        """
        Get current news sentiment score.

        Currently returns a mock/configured value. Will be replaced with real
        sentiment analysis from news APIs.

        Returns:
            Dictionary containing:
                - score: Normalized score 0-100
                - signal: 'fear', 'neutral', or 'greed'
                - source: Where the score came from ('mock', 'config', or future: 'api')
                - reasoning: Explanation of the score
        """
        # Try to load override from config file
        config_score = self._load_config_override()

        if config_score is not None:
            score = config_score
            source = "config"
            logger.info(f"Using config override: {score}")
        else:
            score = self.default_score
            source = "mock"
            logger.debug(f"Using default mock score: {score}")

        # Determine signal based on score
        if score < 45:
            signal = "fear"
            reasoning = "Mock/Config: Negative social sentiment detected"
        elif score <= 55:
            signal = "neutral"
            reasoning = "Mock/Config: Neutral social sentiment (default)"
        else:
            signal = "greed"
            reasoning = "Mock/Config: Positive social sentiment detected"

        return {
            "score": round(score, 2),
            "signal": signal,
            "source": source,
            "reasoning": reasoning,
            "is_mock": True  # Flag to indicate this is not real data yet
        }

    def get_twitter_sentiment(self) -> Dict[str, any]:
        """
        Get Twitter/X sentiment score.

        Placeholder for future Twitter API integration.

        Returns:
            Dictionary with sentiment score (currently returns neutral)
        """
        logger.warning("Twitter sentiment not implemented yet - returning neutral")
        return {
            "score": 50.0,
            "signal": "neutral",
            "source": "mock",
            "reasoning": "Twitter API not yet integrated",
            "is_mock": True
        }

    def get_combined_social_score(self) -> Dict[str, any]:
        """
        Get combined social sentiment from all sources.

        Currently just returns news sentiment. In the future, this will
        aggregate multiple social signal sources (Twitter, Reddit, News, etc.)

        Returns:
            Dictionary containing combined social sentiment
        """
        # For now, just use news sentiment
        # Future: Combine news, twitter, reddit, etc. with weights
        news_sentiment = self.get_news_sentiment()

        logger.info(
            f"Combined Social Score: {news_sentiment['score']:.2f} "
            f"({news_sentiment['signal']}) - Source: {news_sentiment['source']}"
        )

        return {
            **news_sentiment,
            "components": {
                "news": news_sentiment["score"],
                # Future: "twitter": twitter_score, "reddit": reddit_score, etc.
            }
        }

    def _load_config_override(self) -> Optional[float]:
        """
        Load sentiment score override from config file.

        Config file format (JSON):
        {
            "sentiment_override": 75.5,
            "note": "Manual override for testing"
        }

        Returns:
            Override score if found, None otherwise
        """
        try:
            if not self.config_file.exists():
                logger.debug(f"Config file not found: {self.config_file}")
                return None

            with open(self.config_file, "r", encoding="utf-8") as f:
                config = json.load(f)

            override = config.get("sentiment_override")

            if override is not None:
                # Validate override is in valid range
                if 0 <= override <= 100:
                    logger.info(
                        f"Loaded sentiment override from config: {override} "
                        f"(Note: {config.get('note', 'N/A')})"
                    )
                    return float(override)
                else:
                    logger.warning(
                        f"Invalid sentiment override value: {override} "
                        f"(must be 0-100)"
                    )

            return None

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse config file: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading config override: {e}")
            return None

    def set_config_override(self, score: float, note: str = "") -> bool:
        """
        Set a manual sentiment override in the config file.

        Useful for testing different sentiment scenarios.

        Args:
            score: Sentiment score to set (0-100)
            note: Optional note explaining the override

        Returns:
            True if successful, False otherwise
        """
        try:
            if not 0 <= score <= 100:
                logger.error(f"Invalid score: {score} (must be 0-100)")
                return False

            # Ensure config directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            config = {
                "sentiment_override": score,
                "note": note or f"Manual override set to {score}",
                "last_updated": "Manual configuration"
            }

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)

            logger.info(f"Set sentiment override to {score}: {note}")
            return True

        except Exception as e:
            logger.error(f"Failed to set config override: {e}")
            return False
