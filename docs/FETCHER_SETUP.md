# CMC Fetcher Setup and Usage Guide

## Overview

The CMC (CoinMarketCap) Fetcher is the core data acquisition component of the Fear & Greed Index. It retrieves market data from CoinMarketCap's API with built-in rate limiting, error handling, and data persistence.

## Features

✅ **Rate Limiting**: Respects CMC API limits (30 calls/minute on free tier)
✅ **Error Handling**: Automatic retries for 429, 500s, and timeout errors
✅ **Data Persistence**: Saves raw responses to `data/raw/` for debugging
✅ **Logging**: Comprehensive logging for all operations
✅ **Type Hints**: Fully typed for better IDE support
✅ **Async/Await**: Non-blocking async operations
✅ **Resilient**: Exponential backoff and configurable retries

## Setup

### 1. Install Dependencies

Using `uv` (recommended):
```bash
uv pip install -e .
uv pip install -e ".[dev]"
```

Or using standard pip:
```bash
pip install -e .
pip install -e ".[dev]"
```

### 2. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your CoinMarketCap API key:
```env
CMC_API_KEY=your_actual_api_key_here
```

Get your free API key from: https://coinmarketcap.com/api/

## Usage

### Basic Usage

```python
import asyncio
from src.fetchers import CMCFetcher

async def main():
    # Initialize the fetcher
    async with CMCFetcher() as fetcher:
        # Fetch all data (global metrics + crypto quotes)
        data = await fetcher.fetch()
        print(data)

asyncio.run(main())
```

### Fetch Global Metrics Only

```python
async with CMCFetcher() as fetcher:
    global_data = await fetcher.fetch_global_metrics()
    btc_dominance = global_data["data"]["btc_dominance"]
    print(f"BTC Dominance: {btc_dominance}%")
```

### Fetch Specific Cryptocurrencies

```python
async with CMCFetcher() as fetcher:
    # Fetch specific symbols
    btc_data = await fetcher.fetch_crypto_quotes(symbols=["BTC", "ETH"])

    # Or fetch top N by market cap
    top_10 = await fetcher.fetch_crypto_quotes(limit=10)
```

### Health Check

```python
async with CMCFetcher() as fetcher:
    is_healthy = await fetcher.health_check()
    print(f"API is {'available' if is_healthy else 'unavailable'}")
```

### Custom Configuration

```python
from pathlib import Path

fetcher = CMCFetcher(
    api_key="your_key",
    rate_limit_calls=30,      # Max calls per period
    rate_limit_period=60,     # Period in seconds
    data_dir=Path("./custom/data/path")
)
```

## Running Tests

### Run All Tests

```bash
pytest tests/test_cmc_fetcher.py -v
```

### Run Specific Test Classes

```bash
# Test rate limiter only
pytest tests/test_cmc_fetcher.py::TestRateLimiter -v

# Test CMC fetcher only
pytest tests/test_cmc_fetcher.py::TestCMCFetcher -v
```

### Run with Coverage

```bash
pytest tests/test_cmc_fetcher.py --cov=src.fetchers --cov-report=html
```

### Run a Specific Test

```bash
pytest tests/test_cmc_fetcher.py::TestCMCFetcher::test_fetch_global_metrics_success -v
```

## Example Script

Run the included example script to see the fetcher in action:

```bash
python examples/fetch_cmc_data.py
```

This will:
1. Perform a health check
2. Fetch global market metrics
3. Fetch BTC quote data
4. Fetch top 10 cryptocurrencies
5. Use the combined fetch method
6. Save all raw data to `data/raw/`

## Data Storage

Raw API responses are automatically saved to `data/raw/` with timestamps:

```
data/raw/
├── cmc_global_20260205_120000.json
├── cmc_quotes_20260205_120001.json
└── ...
```

File naming format: `cmc_{type}_{YYYYMMDD_HHMMSS}.json`

## API Endpoints

The fetcher uses two CMC endpoints:

1. **Global Metrics**: `/v1/global-metrics/quotes/latest`
   - Returns: BTC dominance, total market cap, total volume, etc.

2. **Cryptocurrency Quotes**: `/v2/cryptocurrency/quotes/latest`
   - Returns: Price, volume, market cap, percent changes for specific coins

## Rate Limiting

The fetcher implements a sliding window rate limiter:

- **Default**: 30 calls per 60 seconds (CMC free tier)
- **Behavior**: Automatically sleeps when limit is reached
- **Configuration**: Adjustable via environment variables

```env
CMC_RATE_LIMIT_CALLS=30
CMC_RATE_LIMIT_PERIOD=60
```

## Error Handling

The fetcher handles various error scenarios:

| Error Type | Behavior |
|------------|----------|
| 429 (Rate Limit) | Waits for `Retry-After` header, then retries |
| 500-599 (Server Error) | Exponential backoff, up to 3 retries |
| Timeout | Exponential backoff, up to 3 retries |
| Connection Error | Exponential backoff, up to 3 retries |
| 4xx (Client Error) | Raises immediately (no retry) |

## Logging

Logs are output to stdout with configurable level:

```env
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR
```

Example log output:
```
2026-02-05 12:00:00 - src.fetchers.cmc_fetcher - INFO - CMCFetcher initialized with rate limit: 30 calls per 60s
2026-02-05 12:00:01 - src.fetchers.cmc_fetcher - INFO - Making request to /v1/global-metrics/quotes/latest (attempt 1/4)
2026-02-05 12:00:02 - src.fetchers.cmc_fetcher - INFO - Successfully fetched data from /v1/global-metrics/quotes/latest
```

## Architecture

```
CMCFetcher
├── RateLimiter (sliding window)
├── HTTP Client (httpx.AsyncClient)
├── fetch_global_metrics()
├── fetch_crypto_quotes()
├── fetch() [combines both]
└── health_check()
```

## Next Steps

After successfully fetching data, the next steps are:

1. **Normalizers**: Transform raw data into 0-100 scores
2. **Aggregator**: Combine normalized metrics into final index
3. **API Layer**: Expose the index via FastAPI endpoints

## Troubleshooting

### API Key Issues

**Error**: `ValueError: CMC_API_KEY must be provided`

**Solution**: Ensure your `.env` file contains a valid CMC API key

### Rate Limiting

**Warning**: `Rate limit reached. Sleeping for X seconds`

**Solution**: This is normal behavior. The fetcher automatically handles rate limits.

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'src'`

**Solution**: Install the package in development mode:
```bash
pip install -e .
```

### Test Failures

**Error**: Tests fail due to missing dependencies

**Solution**: Install dev dependencies:
```bash
pip install -e ".[dev]"
```

## Contributing

When adding new features to the fetcher:

1. Update the `BaseFetcher` interface if needed
2. Add corresponding tests in `tests/test_cmc_fetcher.py`
3. Update this documentation
4. Follow the project's type hinting and logging standards
5. Ensure all tests pass before committing

## Resources

- [CoinMarketCap API Documentation](https://coinmarketcap.com/api/documentation/v1/)
- [Project Architecture](../architecture.md)
- [CLAUDE.md - Project Guidelines](../CLAUDE.md)
