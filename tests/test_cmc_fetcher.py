"""
Tests for the CMC fetcher.

Tests cover rate limiting, error handling, retries, and data persistence.
"""

import asyncio
import json
import os
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

import pytest
import httpx

from src.fetchers.cmc_fetcher import CMCFetcher, RateLimiter


# Test data fixtures
@pytest.fixture
def mock_global_metrics():
    """Mock global metrics response from CMC API."""
    return {
        "status": {
            "timestamp": "2026-02-05T12:00:00.000Z",
            "error_code": 0,
            "error_message": None
        },
        "data": {
            "btc_dominance": 48.5,
            "eth_dominance": 18.2,
            "active_cryptocurrencies": 10000,
            "total_cryptocurrencies": 20000,
            "active_market_pairs": 50000,
            "quote": {
                "USD": {
                    "total_market_cap": 2500000000000,
                    "total_volume_24h": 150000000000,
                    "total_volume_24h_reported": 200000000000,
                    "altcoin_volume_24h": 100000000000,
                    "altcoin_market_cap": 1300000000000
                }
            }
        }
    }


@pytest.fixture
def mock_crypto_quotes():
    """Mock cryptocurrency quotes response from CMC API."""
    return {
        "status": {
            "timestamp": "2026-02-05T12:00:00.000Z",
            "error_code": 0,
            "error_message": None
        },
        "data": {
            "BTC": [{
                "id": 1,
                "name": "Bitcoin",
                "symbol": "BTC",
                "quote": {
                    "USD": {
                        "price": 50000.0,
                        "volume_24h": 30000000000,
                        "volume_change_24h": 5.5,
                        "percent_change_1h": 0.5,
                        "percent_change_24h": 2.3,
                        "percent_change_7d": 8.1,
                        "market_cap": 950000000000,
                        "market_cap_dominance": 48.5
                    }
                }
            }]
        }
    }


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary directory for test data."""
    data_dir = tmp_path / "data" / "raw"
    data_dir.mkdir(parents=True)
    return data_dir


@pytest.fixture
async def cmc_fetcher(temp_data_dir):
    """Create a CMC fetcher instance with test configuration."""
    fetcher = CMCFetcher(
        api_key="test_api_key_12345",
        rate_limit_calls=5,
        rate_limit_period=10,
        data_dir=temp_data_dir
    )
    yield fetcher
    await fetcher.close()


class TestRateLimiter:
    """Tests for the RateLimiter class."""

    @pytest.mark.asyncio
    async def test_rate_limiter_allows_calls_within_limit(self):
        """Test that rate limiter allows calls within the limit."""
        limiter = RateLimiter(max_calls=3, period=1)

        start = asyncio.get_event_loop().time()
        for _ in range(3):
            await limiter.acquire()
        elapsed = asyncio.get_event_loop().time() - start

        # Should complete almost instantly
        assert elapsed < 0.5

    @pytest.mark.asyncio
    async def test_rate_limiter_blocks_when_limit_exceeded(self):
        """Test that rate limiter blocks when limit is exceeded."""
        limiter = RateLimiter(max_calls=2, period=1)

        # Make 2 calls (within limit)
        await limiter.acquire()
        await limiter.acquire()

        # Third call should block
        start = asyncio.get_event_loop().time()
        await limiter.acquire()
        elapsed = asyncio.get_event_loop().time() - start

        # Should have waited at least 1 second
        assert elapsed >= 1.0

    @pytest.mark.asyncio
    async def test_rate_limiter_sliding_window(self):
        """Test that rate limiter uses a sliding window."""
        limiter = RateLimiter(max_calls=2, period=2)

        await limiter.acquire()
        await asyncio.sleep(1.1)
        await limiter.acquire()

        # This should not block because the first call is more than 1 second old
        # but still within the 2-second window
        start = asyncio.get_event_loop().time()
        await limiter.acquire()
        elapsed = asyncio.get_event_loop().time() - start

        # Should have waited at least 0.8 seconds (2 - 1.1 - buffer)
        assert elapsed >= 0.8


class TestCMCFetcher:
    """Tests for the CMCFetcher class."""

    @pytest.mark.asyncio
    async def test_initialization_with_api_key(self, temp_data_dir):
        """Test fetcher initialization with API key."""
        fetcher = CMCFetcher(
            api_key="test_key",
            data_dir=temp_data_dir
        )
        assert fetcher.api_key == "test_key"
        await fetcher.close()

    @pytest.mark.asyncio
    async def test_initialization_without_api_key_raises_error(self, temp_data_dir):
        """Test that initialization fails without API key."""
        # Ensure environment variable is not set
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="CMC_API_KEY must be provided"):
                CMCFetcher(data_dir=temp_data_dir)

    @pytest.mark.asyncio
    async def test_fetch_global_metrics_success(
        self,
        cmc_fetcher,
        mock_global_metrics
    ):
        """Test successful fetch of global metrics."""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_global_metrics
        mock_response.raise_for_status = Mock()

        with patch.object(cmc_fetcher.client, 'get', return_value=mock_response):
            result = await cmc_fetcher.fetch_global_metrics()

        assert result == mock_global_metrics
        assert result["data"]["btc_dominance"] == 48.5

    @pytest.mark.asyncio
    async def test_fetch_crypto_quotes_with_symbols(
        self,
        cmc_fetcher,
        mock_crypto_quotes
    ):
        """Test successful fetch of crypto quotes with specific symbols."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_crypto_quotes
        mock_response.raise_for_status = Mock()

        with patch.object(cmc_fetcher.client, 'get', return_value=mock_response) as mock_get:
            result = await cmc_fetcher.fetch_crypto_quotes(symbols=["BTC"])

        assert result == mock_crypto_quotes
        # Verify the correct parameters were passed
        call_args = mock_get.call_args
        assert "symbol" in call_args[1]["params"]
        assert call_args[1]["params"]["symbol"] == "BTC"

    @pytest.mark.asyncio
    async def test_fetch_crypto_quotes_top_n(
        self,
        cmc_fetcher,
        mock_crypto_quotes
    ):
        """Test fetch of top N cryptocurrencies."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_crypto_quotes
        mock_response.raise_for_status = Mock()

        with patch.object(cmc_fetcher.client, 'get', return_value=mock_response) as mock_get:
            result = await cmc_fetcher.fetch_crypto_quotes(limit=5)

        # Verify the correct parameters were passed
        call_args = mock_get.call_args
        assert "limit" in call_args[1]["params"]
        assert call_args[1]["params"]["limit"] == 5

    @pytest.mark.asyncio
    async def test_fetch_combines_all_data(
        self,
        cmc_fetcher,
        mock_global_metrics,
        mock_crypto_quotes
    ):
        """Test that fetch() combines global metrics and crypto quotes."""
        mock_response_global = Mock()
        mock_response_global.status_code = 200
        mock_response_global.json.return_value = mock_global_metrics
        mock_response_global.raise_for_status = Mock()

        mock_response_quotes = Mock()
        mock_response_quotes.status_code = 200
        mock_response_quotes.json.return_value = mock_crypto_quotes
        mock_response_quotes.raise_for_status = Mock()

        # Mock both endpoints
        responses = [mock_response_global, mock_response_quotes]
        with patch.object(
            cmc_fetcher.client,
            'get',
            side_effect=responses
        ):
            result = await cmc_fetcher.fetch()

        assert "global_metrics" in result
        assert "crypto_quotes" in result
        assert "timestamp" in result
        assert result["global_metrics"] == mock_global_metrics
        assert result["crypto_quotes"] == mock_crypto_quotes

    @pytest.mark.asyncio
    async def test_retry_on_429_rate_limit(self, cmc_fetcher, mock_global_metrics):
        """Test that fetcher retries on 429 rate limit response."""
        # First response: 429, second response: success
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {"Retry-After": "1"}

        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = mock_global_metrics
        mock_response_success.raise_for_status = Mock()

        with patch.object(
            cmc_fetcher.client,
            'get',
            side_effect=[mock_response_429, mock_response_success]
        ):
            result = await cmc_fetcher.fetch_global_metrics()

        assert result == mock_global_metrics

    @pytest.mark.asyncio
    async def test_retry_on_500_server_error(self, cmc_fetcher, mock_global_metrics):
        """Test that fetcher retries on 500 server error."""
        # First response: 500, second response: success
        mock_response_500 = Mock()
        mock_response_500.status_code = 500

        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = mock_global_metrics
        mock_response_success.raise_for_status = Mock()

        with patch.object(
            cmc_fetcher.client,
            'get',
            side_effect=[mock_response_500, mock_response_success]
        ):
            result = await cmc_fetcher.fetch_global_metrics()

        assert result == mock_global_metrics

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, cmc_fetcher):
        """Test that fetcher raises error after max retries."""
        # All responses fail with 500
        mock_response_500 = Mock()
        mock_response_500.status_code = 500
        mock_response_500.raise_for_status = Mock(
            side_effect=httpx.HTTPStatusError(
                "Server Error",
                request=Mock(),
                response=mock_response_500
            )
        )

        with patch.object(
            cmc_fetcher.client,
            'get',
            return_value=mock_response_500
        ):
            with pytest.raises(httpx.HTTPStatusError):
                await cmc_fetcher.fetch_global_metrics()

    @pytest.mark.asyncio
    async def test_timeout_retry(self, cmc_fetcher, mock_global_metrics):
        """Test that fetcher retries on timeout."""
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = mock_global_metrics
        mock_response_success.raise_for_status = Mock()

        with patch.object(
            cmc_fetcher.client,
            'get',
            side_effect=[
                httpx.TimeoutException("Timeout"),
                mock_response_success
            ]
        ):
            result = await cmc_fetcher.fetch_global_metrics()

        assert result == mock_global_metrics

    @pytest.mark.asyncio
    async def test_data_persistence(
        self,
        cmc_fetcher,
        mock_global_metrics,
        temp_data_dir
    ):
        """Test that raw data is saved to disk."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_global_metrics
        mock_response.raise_for_status = Mock()

        with patch.object(cmc_fetcher.client, 'get', return_value=mock_response):
            await cmc_fetcher.fetch_global_metrics()

        # Check that a file was created
        files = list(temp_data_dir.glob("cmc_global_*.json"))
        assert len(files) == 1

        # Verify the file contents
        with open(files[0]) as f:
            saved_data = json.load(f)
        assert saved_data == mock_global_metrics

    @pytest.mark.asyncio
    async def test_health_check_success(self, cmc_fetcher, mock_global_metrics):
        """Test successful health check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_global_metrics
        mock_response.raise_for_status = Mock()

        with patch.object(cmc_fetcher.client, 'get', return_value=mock_response):
            result = await cmc_fetcher.health_check()

        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, cmc_fetcher):
        """Test failed health check."""
        with patch.object(
            cmc_fetcher.client,
            'get',
            side_effect=httpx.RequestError("Connection failed")
        ):
            result = await cmc_fetcher.health_check()

        assert result is False

    @pytest.mark.asyncio
    async def test_context_manager(self, temp_data_dir, mock_global_metrics):
        """Test that fetcher works as async context manager."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_global_metrics
        mock_response.raise_for_status = Mock()

        async with CMCFetcher(
            api_key="test_key",
            data_dir=temp_data_dir
        ) as fetcher:
            with patch.object(fetcher.client, 'get', return_value=mock_response):
                result = await fetcher.fetch_global_metrics()
            assert result == mock_global_metrics

        # Verify client was closed
        assert fetcher.client.is_closed
