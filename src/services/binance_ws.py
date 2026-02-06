"""
Binance WebSocket Service - Real-time Multi-Asset Price Monitoring.

This module connects to Binance WebSocket API for live BTC/ETH/SOL prices
and detects intelligent volatility crashes with per-asset thresholds.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, List
from collections import deque

import websockets
import json

logger = logging.getLogger(__name__)


class PriceMonitor:
    """
    Monitors price movements for a single asset with intelligent drop detection.

    Uses a 5-minute rolling buffer (approx 300 data points) to detect quick drops.
    """

    def __init__(self, asset: str, drop_threshold_percent: float, buffer_maxlen: int = 300):
        """
        Initialize price monitor for an asset.

        Args:
            asset: Asset symbol (e.g., "BTC", "ETH", "SOL")
            drop_threshold_percent: Percentage drop to trigger alert
            buffer_maxlen: Maximum number of prices to store (300 ≈ 5 mins)
        """
        self.asset = asset
        self.drop_threshold_percent = drop_threshold_percent
        self.price_buffer: deque = deque(maxlen=buffer_maxlen)
        self.current_price: Optional[float] = None

    def add_price(self, price: float) -> Optional[Dict]:
        """
        Add a new price and check for quick drops.

        Args:
            price: Current asset price in USDT

        Returns:
            Volatility crash event dict if threshold exceeded, None otherwise
        """
        now = datetime.now()
        self.price_buffer.append((now, price))
        self.current_price = price

        if len(self.price_buffer) < 10:  # Need minimum data
            return None

        # Get the highest price in the buffer
        max_price = max(p for _, p in self.price_buffer)

        # Calculate drop percentage from peak
        drop_percent = ((max_price - price) / max_price) * 100

        # Check if drop exceeds threshold
        if drop_percent >= self.drop_threshold_percent:
            return {
                "asset": self.asset,
                "type": "VOLATILITY_CRASH",
                "magnitude": drop_percent,
                "current_price": price,
                "peak_price": max_price,
                "price_drop": max_price - price,
                "timestamp": now.isoformat(),
                "buffer_size": len(self.price_buffer)
            }

        return None

    def get_current_price(self) -> Optional[float]:
        """Get the most recent price."""
        return self.current_price


class VolatilityDetector:
    """Legacy volatility detector for BTC - kept for backwards compatibility."""

    def __init__(self, window_minutes: int = 10, threshold_usd: float = 500.0):
        """
        Initialize volatility detector.

        Args:
            window_minutes: Time window for volatility detection
            threshold_usd: Price movement threshold in USD
        """
        self.window_minutes = window_minutes
        self.threshold_usd = threshold_usd
        self.price_history: deque = deque(maxlen=1000)  # Store (timestamp, price) tuples

    def add_price(self, price: float) -> Optional[Dict]:
        """
        Add a new price and check for volatility.

        Args:
            price: Current BTC price in USDT

        Returns:
            Volatility event dict if threshold exceeded, None otherwise
        """
        now = datetime.now()
        self.price_history.append((now, price))

        # Get cutoff time for the window
        cutoff = now - timedelta(minutes=self.window_minutes)

        # Find prices within the window
        window_prices = [p for ts, p in self.price_history if ts >= cutoff]

        if len(window_prices) < 2:
            return None

        min_price = min(window_prices)
        max_price = max(window_prices)
        price_change = max_price - min_price

        # Check if threshold exceeded
        if price_change >= self.threshold_usd:
            change_percent = (price_change / min_price) * 100

            return {
                "type": "volatility_spike",
                "asset": "BTC",
                "current_price": price,
                "min_price": min_price,
                "max_price": max_price,
                "price_change": price_change,
                "change_percent": change_percent,
                "window_minutes": self.window_minutes,
                "timestamp": now.isoformat(),
                "volatility_alert": True
            }

        return None


class BinanceWebSocketService:
    """
    Manages WebSocket connection to Binance for real-time multi-asset price updates.

    Features:
    - Real-time BTC/ETH/SOL USDT price streaming via Combined Stream
    - Intelligent per-asset volatility crash detection
    - Automatic reconnection on disconnect
    - Event broadcasting to subscribers
    """

    def __init__(
        self,
        window_minutes: int = 10,
        threshold_usd: float = 500.0
    ):
        """
        Initialize Binance WebSocket service.

        Args:
            window_minutes: Legacy volatility detection window (for BTC)
            threshold_usd: Legacy volatility threshold in USD (for BTC)
        """
        # Combined Stream URL for BTC, ETH, and SOL
        self.ws_url = "wss://stream.binance.com:9443/stream?streams=btcusdt@trade/ethusdt@trade/solusdt@trade"

        self.is_running = False

        # Legacy BTC volatility detector
        self.volatility_detector = VolatilityDetector(window_minutes, threshold_usd)

        # Multi-Asset Price Monitors with intelligent thresholds
        self.price_monitors = {
            "BTC": PriceMonitor("BTC", drop_threshold_percent=0.5, buffer_maxlen=300),
            "ETH": PriceMonitor("ETH", drop_threshold_percent=1.0, buffer_maxlen=300),
            "SOL": PriceMonitor("SOL", drop_threshold_percent=2.0, buffer_maxlen=300),
        }

        # Subscribers for different event types
        self.price_subscribers: List[Callable] = []
        self.volatility_subscribers: List[Callable] = []
        self.crash_subscribers: List[Callable] = []  # New: for VOLATILITY_CRASH events

    def subscribe_price(self, callback: Callable):
        """Subscribe to price updates."""
        self.price_subscribers.append(callback)

    def subscribe_volatility(self, callback: Callable):
        """Subscribe to legacy volatility events (BTC only)."""
        self.volatility_subscribers.append(callback)

    def subscribe_crash(self, callback: Callable):
        """Subscribe to VOLATILITY_CRASH events (multi-asset)."""
        self.crash_subscribers.append(callback)

    async def _broadcast_price(self, price_data: Dict):
        """Broadcast price update to all subscribers."""
        for callback in self.price_subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(price_data)
                else:
                    callback(price_data)
            except Exception as e:
                logger.error(f"Error in price subscriber: {e}")

    async def _broadcast_volatility(self, volatility_data: Dict):
        """Broadcast volatility event to all subscribers."""
        for callback in self.volatility_subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(volatility_data)
                else:
                    callback(volatility_data)
            except Exception as e:
                logger.error(f"Error in volatility subscriber: {e}")

    async def _broadcast_crash(self, crash_data: Dict):
        """Broadcast VOLATILITY_CRASH event to all subscribers."""
        for callback in self.crash_subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(crash_data)
                else:
                    callback(crash_data)
            except Exception as e:
                logger.error(f"Error in crash subscriber: {e}")

    async def _process_message(self, message: str):
        """
        Process incoming WebSocket message from Binance Combined Stream.

        Args:
            message: Raw JSON message from Binance Combined Stream
        """
        try:
            msg = json.loads(message)

            # Combined stream format: {"stream": "btcusdt@trade", "data": {...}}
            if "stream" in msg and "data" in msg:
                stream_name = msg["stream"]
                data = msg["data"]

                # Extract asset symbol from stream name
                # e.g., "btcusdt@trade" -> "BTC"
                symbol = data.get("s", "")  # Full symbol like "BTCUSDT"
                asset = symbol.replace("USDT", "")  # Extract "BTC", "ETH", "SOL"

                # Extract price
                if "p" in data:
                    price = float(data["p"])

                    # Create price update event
                    price_event = {
                        "type": "price_update",
                        "asset": asset,
                        "symbol": symbol,
                        "price": price,
                        "quantity": float(data.get("q", 0)),
                        "timestamp": datetime.fromtimestamp(data.get("T", 0) / 1000).isoformat()
                    }

                    # Broadcast price update
                    await self._broadcast_price(price_event)

                    # Check asset-specific price monitor for quick drops
                    if asset in self.price_monitors:
                        monitor = self.price_monitors[asset]
                        crash_event = monitor.add_price(price)

                        if crash_event:
                            logger.warning(
                                f"🚨 {asset} VOLATILITY_CRASH detected! "
                                f"Dropped {crash_event['magnitude']:.2f}% "
                                f"from ${crash_event['peak_price']:.2f} to ${crash_event['current_price']:.2f}"
                            )
                            await self._broadcast_crash(crash_event)

                    # Legacy BTC volatility detector (backwards compatibility)
                    if asset == "BTC":
                        volatility_event = self.volatility_detector.add_price(price)
                        if volatility_event:
                            logger.warning(
                                f"🚨 Legacy volatility spike detected! "
                                f"Price moved ${volatility_event['price_change']:.2f} "
                                f"({volatility_event['change_percent']:.2f}%) "
                                f"in {volatility_event['window_minutes']} minutes"
                            )
                            await self._broadcast_volatility(volatility_event)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse WebSocket message: {e}")
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")

    async def start(self):
        """
        Start the WebSocket connection and begin streaming.

        Automatically reconnects on disconnect.
        """
        self.is_running = True

        while self.is_running:
            try:
                logger.info(f"Connecting to Binance WebSocket: {self.ws_url}")

                async with websockets.connect(self.ws_url) as websocket:
                    logger.info("✅ Connected to Binance WebSocket")

                    while self.is_running:
                        try:
                            message = await asyncio.wait_for(
                                websocket.recv(),
                                timeout=30.0
                            )
                            await self._process_message(message)

                        except asyncio.TimeoutError:
                            # Send ping to keep connection alive
                            await websocket.ping()

            except websockets.exceptions.ConnectionClosed:
                if self.is_running:
                    logger.warning("WebSocket connection closed. Reconnecting in 5s...")
                    await asyncio.sleep(5)
            except Exception as e:
                if self.is_running:
                    logger.error(f"WebSocket error: {e}. Reconnecting in 5s...")
                    await asyncio.sleep(5)

        logger.info("Binance WebSocket service stopped")

    async def stop(self):
        """Stop the WebSocket service."""
        logger.info("Stopping Binance WebSocket service...")
        self.is_running = False

    def get_current_price(self, asset: str = "BTC") -> Optional[float]:
        """
        Get the most recent price for a specific asset.

        Args:
            asset: Asset symbol ("BTC", "ETH", "SOL")

        Returns:
            Current price or None if not available
        """
        if asset in self.price_monitors:
            return self.price_monitors[asset].get_current_price()
        return None

    def get_all_prices(self) -> Dict[str, Optional[float]]:
        """
        Get current prices for all monitored assets.

        Returns:
            Dictionary mapping asset symbols to their current prices
        """
        return {
            asset: monitor.get_current_price()
            for asset, monitor in self.price_monitors.items()
        }


# Global instance for use across the application
_binance_service: Optional[BinanceWebSocketService] = None


def get_binance_service() -> BinanceWebSocketService:
    """Get or create the global Binance WebSocket service instance."""
    global _binance_service
    if _binance_service is None:
        _binance_service = BinanceWebSocketService(
            window_minutes=10,
            threshold_usd=500.0
        )
    return _binance_service
