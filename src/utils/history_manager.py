"""
History persistence manager for market data.

This module provides utilities to save and load historical market data
for trend analysis and historical scoring.
"""

import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class HistoryManager:
    """
    Manage historical market data persistence.

    Saves total market cap and BTC dominance to CSV for trend analysis.
    """

    def __init__(self, history_file: Optional[Path] = None):
        """
        Initialize the history manager.

        Args:
            history_file: Path to CSV file (defaults to data/processed/market_history.csv)
        """
        self.history_file = history_file or Path("data/processed/market_history.csv")
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize CSV with headers if it doesn't exist
        if not self.history_file.exists():
            self._initialize_csv()
            logger.info(f"Created new history file: {self.history_file}")
        else:
            logger.info(f"Using existing history file: {self.history_file}")

    def _initialize_csv(self) -> None:
        """Create CSV file with headers."""
        headers = [
            "timestamp",
            "total_market_cap",
            "btc_dominance",
            "total_volume_24h",
            "market_cap_change_24h"
        ]

        with open(self.history_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

        logger.debug("Initialized CSV file with headers")

    def save_snapshot(
        self,
        total_market_cap: float,
        btc_dominance: float,
        total_volume_24h: Optional[float] = None,
        market_cap_change_24h: Optional[float] = None,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """
        Save a market data snapshot to history.

        Args:
            total_market_cap: Total cryptocurrency market cap in USD
            btc_dominance: Bitcoin dominance percentage (0-100)
            total_volume_24h: Total 24h trading volume in USD (optional)
            market_cap_change_24h: 24h percentage change (optional)
            timestamp: Timestamp of the snapshot (defaults to now)

        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            timestamp = timestamp or datetime.now()

            row = [
                timestamp.isoformat(),
                total_market_cap,
                btc_dominance,
                total_volume_24h if total_volume_24h is not None else "",
                market_cap_change_24h if market_cap_change_24h is not None else ""
            ]

            with open(self.history_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(row)

            logger.info(
                f"[OK] Data Saved Successfully - "
                f"Market Cap: ${total_market_cap:,.0f}, "
                f"BTC Dominance: {btc_dominance:.2f}%"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to save snapshot: {e}")
            return False

    def load_history(
        self,
        limit: Optional[int] = None
    ) -> List[Dict[str, any]]:
        """
        Load historical market data.

        Args:
            limit: Maximum number of records to load (most recent first)

        Returns:
            List of dictionaries containing historical data
        """
        try:
            history = []

            with open(self.history_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert numeric fields
                    record = {
                        "timestamp": row["timestamp"],
                        "total_market_cap": float(row["total_market_cap"]),
                        "btc_dominance": float(row["btc_dominance"])
                    }

                    # Add optional fields if present
                    if row["total_volume_24h"]:
                        record["total_volume_24h"] = float(row["total_volume_24h"])

                    if row["market_cap_change_24h"]:
                        record["market_cap_change_24h"] = float(row["market_cap_change_24h"])

                    history.append(record)

            # Return most recent records first
            history.reverse()

            if limit:
                history = history[:limit]

            logger.info(f"Loaded {len(history)} historical records")
            return history

        except FileNotFoundError:
            logger.warning(f"History file not found: {self.history_file}")
            return []
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            return []

    def get_latest(self) -> Optional[Dict[str, any]]:
        """
        Get the most recent market data snapshot.

        Returns:
            Dictionary containing the latest snapshot or None if no history
        """
        history = self.load_history(limit=1)
        return history[0] if history else None

    def calculate_trend(
        self,
        field: str,
        periods: int = 7
    ) -> Optional[float]:
        """
        Calculate trend for a specific field over N periods.

        Args:
            field: Field name ('total_market_cap' or 'btc_dominance')
            periods: Number of historical periods to analyze

        Returns:
            Average percentage change per period, or None if insufficient data
        """
        try:
            history = self.load_history(limit=periods + 1)

            if len(history) < 2:
                logger.warning(f"Insufficient data for trend calculation (need 2+, have {len(history)})")
                return None

            values = [record[field] for record in history if field in record]

            if len(values) < 2:
                return None

            # Calculate percentage changes
            changes = []
            for i in range(len(values) - 1):
                if values[i] != 0:
                    change = ((values[i] - values[i + 1]) / values[i + 1]) * 100
                    changes.append(change)

            avg_change = sum(changes) / len(changes) if changes else 0

            logger.debug(
                f"Trend for {field}: {avg_change:.2f}% avg change over {len(changes)} periods"
            )

            return round(avg_change, 2)

        except Exception as e:
            logger.error(f"Failed to calculate trend: {e}")
            return None

    def get_stats(self) -> Dict[str, any]:
        """
        Get statistics about the history file.

        Returns:
            Dictionary with record count, date range, and file size
        """
        try:
            history = self.load_history()

            if not history:
                return {
                    "record_count": 0,
                    "file_exists": self.history_file.exists()
                }

            return {
                "record_count": len(history),
                "oldest_record": history[-1]["timestamp"],
                "newest_record": history[0]["timestamp"],
                "file_size_bytes": self.history_file.stat().st_size,
                "file_path": str(self.history_file)
            }

        except Exception as e:
            logger.error(f"Failed to get history stats: {e}")
            return {"error": str(e)}
