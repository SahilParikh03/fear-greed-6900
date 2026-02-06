"""
CoinMarketCap API fetcher with rate limiting and error handling.

This module provides the CMCFetcher class for retrieving market data from
CoinMarketCap's API, including global metrics and cryptocurrency quotes.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from collections import deque
from time import time

import httpx
from dotenv import load_dotenv

from .base import BaseFetcher

# Load environment variables
load_dotenv(override=True)

# Fallback: Manually read .env file if CMC_API_KEY not found
if not os.getenv("CMC_API_KEY"):
    print("[DEBUG] CMC_API_KEY not found in environment, attempting manual .env read")
    env_file = Path(__file__).parent.parent.parent / ".env"
    if env_file.exists():
        print(f"[DEBUG] Found .env file at: {env_file}")
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()
        print(f"[DEBUG] Manually loaded environment variables from {env_file}")
    else:
        print(f"[DEBUG] No .env file found at {env_file}")

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter to enforce API call limits.

    Uses a sliding window approach to track API calls and ensure we don't
    exceed the rate limit (default: 30 calls per 60 seconds for CMC free tier).
    """

    def __init__(self, max_calls: int, period: int):
        """
        Initialize the rate limiter.

        Args:
            max_calls: Maximum number of calls allowed in the period
            period: Time period in seconds
        """
        self.max_calls = max_calls
        self.period = period
        self.calls: deque = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """
        Acquire permission to make an API call.

        Blocks if the rate limit would be exceeded until a slot becomes available.
        """
        async with self._lock:
            now = time()

            # Remove calls outside the current window
            while self.calls and self.calls[0] < now - self.period:
                self.calls.popleft()

            # If at limit, wait until the oldest call expires
            if len(self.calls) >= self.max_calls:
                sleep_time = self.period - (now - self.calls[0]) + 0.1
                logger.info(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds")
                await asyncio.sleep(sleep_time)
                # Recursively try again
                return await self.acquire()

            # Record this call
            self.calls.append(now)


def rate_limited(func: Callable) -> Callable:
    """
    Decorator to apply rate limiting to async class methods.

    This decorator expects to be used on methods of a class that has
    a 'rate_limiter' attribute (RateLimiter instance).

    Args:
        func: The async method to decorate

    Returns:
        Decorated method that respects rate limits
    """
    @wraps(func)
    async def wrapper(self, *args: Any, **kwargs: Any) -> Any:
        # Get the rate limiter from the instance
        await self.rate_limiter.acquire()
        return await func(self, *args, **kwargs)
    return wrapper


class CMCFetcher(BaseFetcher):
    """
    Fetcher for CoinMarketCap API data.

    Retrieves global market metrics and cryptocurrency quotes with proper
    rate limiting, error handling, and data persistence.
    """

    BASE_URL = "https://pro-api.coinmarketcap.com"
    GLOBAL_METRICS_ENDPOINT = "/v1/global-metrics/quotes/latest"
    CRYPTO_QUOTES_ENDPOINT = "/v2/cryptocurrency/quotes/latest"

    def __init__(
        self,
        api_key: Optional[str] = None,
        rate_limit_calls: Optional[int] = None,
        rate_limit_period: Optional[int] = None,
        data_dir: Optional[Path] = None
    ):
        """
        Initialize the CMC fetcher.

        Args:
            api_key: CoinMarketCap API key (defaults to CMC_API_KEY env var)
            rate_limit_calls: Max calls per period (defaults to CMC_RATE_LIMIT_CALLS env var or 30)
            rate_limit_period: Period in seconds (defaults to CMC_RATE_LIMIT_PERIOD env var or 60)
            data_dir: Directory to save raw data (defaults to ./data/raw/)
        """
        # Debug: Show current working directory
        print(f"[DEBUG] Current working directory: {os.getcwd()}")

        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("CMC_API_KEY")

        # Debug: Show if API key was found (masked for safety)
        if self.api_key:
            masked_key = self.api_key[:8] + "..." + self.api_key[-4:] if len(self.api_key) > 12 else "***"
            print(f"[DEBUG] CMC_API_KEY found: {masked_key}")
        else:
            print("[DEBUG] CMC_API_KEY NOT found - checked environment variables")

        if not self.api_key:
            raise ValueError("CMC_API_KEY must be provided or set in environment variables")

        # Rate limiting configuration
        rate_calls = rate_limit_calls or int(os.getenv("CMC_RATE_LIMIT_CALLS", "30"))
        rate_period = rate_limit_period or int(os.getenv("CMC_RATE_LIMIT_PERIOD", "60"))
        self.rate_limiter = RateLimiter(max_calls=rate_calls, period=rate_period)

        # Data directory setup
        self.data_dir = data_dir or Path("./data/raw")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # HTTP client configuration
        self.client = httpx.AsyncClient(
            headers={
                "X-CMC_PRO_API_KEY": self.api_key,
                "Accept": "application/json"
            },
            timeout=30.0
        )

        logger.info(
            f"CMCFetcher initialized with rate limit: {rate_calls} calls per {rate_period}s"
        )

    async def __aenter__(self) -> "CMCFetcher":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
        logger.info("CMCFetcher closed")

    def _save_raw_data(self, data: Dict[str, Any], data_type: str) -> None:
        """
        Save raw API response to disk for debugging.

        Args:
            data: Raw data to save
            data_type: Type identifier (e.g., 'global', 'quotes')
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.data_dir / f"cmc_{data_type}_{timestamp}.json"

        try:
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved raw data to {filename}")
        except Exception as e:
            logger.error(f"Failed to save raw data: {e}")

    @rate_limited
    async def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Make a rate-limited request to the CMC API with retry logic.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            max_retries: Maximum number of retry attempts

        Returns:
            API response as dictionary

        Raises:
            httpx.HTTPStatusError: For non-retryable HTTP errors
            httpx.RequestError: For connection errors
        """
        url = f"{self.BASE_URL}{endpoint}"
        retries = 0

        while retries <= max_retries:
            try:
                logger.info(f"Making request to {endpoint} (attempt {retries + 1}/{max_retries + 1})")
                response = await self.client.get(url, params=params)

                # Check for rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", "60"))
                    logger.warning(f"Rate limited (429). Waiting {retry_after}s before retry")
                    await asyncio.sleep(retry_after)
                    retries += 1
                    continue

                # Check for server errors (5xx)
                if 500 <= response.status_code < 600:
                    if retries < max_retries:
                        wait_time = 2 ** retries  # Exponential backoff
                        logger.warning(
                            f"Server error {response.status_code}. "
                            f"Retrying in {wait_time}s (attempt {retries + 1}/{max_retries})"
                        )
                        await asyncio.sleep(wait_time)
                        retries += 1
                        continue
                    else:
                        logger.error(f"Max retries exceeded for server error {response.status_code}")
                        response.raise_for_status()

                # Raise for other HTTP errors (4xx)
                response.raise_for_status()

                # Success
                data = response.json()
                logger.info(f"Successfully fetched data from {endpoint}")
                return data

            except httpx.TimeoutException as e:
                if retries < max_retries:
                    wait_time = 2 ** retries
                    logger.warning(f"Request timeout. Retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                    retries += 1
                    continue
                else:
                    logger.error(f"Max retries exceeded due to timeout: {e}")
                    raise

            except httpx.RequestError as e:
                if retries < max_retries:
                    wait_time = 2 ** retries
                    logger.warning(f"Connection error: {e}. Retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                    retries += 1
                    continue
                else:
                    logger.error(f"Max retries exceeded due to connection error: {e}")
                    raise

        # Should not reach here, but just in case
        raise Exception(f"Failed to fetch data from {endpoint} after {max_retries} retries")

    async def fetch_global_metrics(self) -> Dict[str, Any]:
        """
        Fetch global market metrics from CMC.

        Returns BTC dominance, total market volume, and other global metrics.

        Returns:
            Dictionary containing global market metrics

        Raises:
            Exception: If the request fails after all retries
        """
        try:
            data = await self._make_request(self.GLOBAL_METRICS_ENDPOINT)
            self._save_raw_data(data, "global")
            return data
        except Exception as e:
            logger.error(f"Failed to fetch global metrics: {e}")
            raise

    async def fetch_crypto_quotes(
        self,
        symbols: Optional[List[str]] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Fetch cryptocurrency quotes from CMC.

        Gets price data for specified cryptocurrencies or top N by market cap.

        Args:
            symbols: List of cryptocurrency symbols (e.g., ['BTC', 'ETH'])
                    If None, fetches top coins by market cap
            limit: Number of top coins to fetch if symbols not specified

        Returns:
            Dictionary containing cryptocurrency quotes

        Raises:
            Exception: If the request fails after all retries
        """
        try:
            params: Dict[str, Any] = {}

            if symbols:
                # Fetch specific symbols
                params["symbol"] = ",".join(symbols)
                logger.info(f"Fetching quotes for symbols: {symbols}")
            else:
                # Fetch top N coins by market cap
                params["limit"] = limit
                logger.info(f"Fetching top {limit} coins by market cap")

            data = await self._make_request(self.CRYPTO_QUOTES_ENDPOINT, params=params)
            self._save_raw_data(data, "quotes")
            return data
        except Exception as e:
            logger.error(f"Failed to fetch crypto quotes: {e}")
            raise

    async def fetch(self) -> Dict[str, Any]:
        """
        Fetch all required data from CMC API.

        This is the main method that implements the BaseFetcher interface.
        It fetches both global metrics and cryptocurrency quotes.

        Returns:
            Dictionary containing:
                - global_metrics: Global market data
                - crypto_quotes: Quote data for BTC and top 10 coins

        Raises:
            Exception: If any fetch operation fails
        """
        logger.info("Starting CMC data fetch")

        try:
            # Fetch global metrics and crypto quotes in parallel
            global_metrics_task = self.fetch_global_metrics()
            crypto_quotes_task = self.fetch_crypto_quotes(
                symbols=["BTC"],  # Always include BTC
                limit=10  # Plus top 10 by market cap
            )

            global_metrics, crypto_quotes = await asyncio.gather(
                global_metrics_task,
                crypto_quotes_task
            )

            result = {
                "timestamp": datetime.now().isoformat(),
                "global_metrics": global_metrics,
                "crypto_quotes": crypto_quotes
            }

            logger.info("CMC data fetch completed successfully")
            return result

        except Exception as e:
            logger.error(f"CMC fetch failed: {e}")
            raise

    async def health_check(self) -> bool:
        """
        Check if the CMC API is accessible.

        Returns:
            bool: True if API is accessible, False otherwise
        """
        try:
            await self._make_request(self.GLOBAL_METRICS_ENDPOINT)
            logger.info("CMC API health check passed")
            return True
        except Exception as e:
            logger.error(f"CMC API health check failed: {e}")
            return False
