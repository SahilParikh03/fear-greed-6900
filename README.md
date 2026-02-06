# Fear & Greed Index 6900 🚀

A modular, custom Crypto Fear & Greed Index using CoinMarketCap API data and advanced sentiment features.

## Quick Start

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. **Install uv** (if not already installed):
   ```bash
   # On Windows (PowerShell)
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

   # On macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Set up the project**:
   ```bash
   # Create virtual environment and install dependencies
   uv sync

   # Or manually
   uv venv
   uv pip install -e .
   ```

3. **Configure environment**:
   ```bash
   # Copy the example env file
   cp .env.example .env

   # Edit .env and add your CoinMarketCap API key
   # Get a free API key from: https://coinmarketcap.com/api/
   ```

4. **Run the development server**:
   ```bash
   uv run uvicorn src.api.main:app --reload
   ```

## Project Structure

```
fear-greed-6900/
├── src/
│   ├── fetchers/        # Data fetchers (CMC, social, etc.)
│   ├── normalizers/     # Data normalization logic
│   ├── aggregator/      # Index calculation "brain"
│   ├── api/            # FastAPI routes
│   └── utils/          # Shared utilities
├── tests/              # All test files
├── config/             # Configuration files
├── data/               # Local database
├── CLAUDE.md           # Project memory & rules
├── plan.md             # Development roadmap
└── architecture.md     # System architecture

```

## Development

### Adding Dependencies
```bash
# Always use uv add (never manually edit pyproject.toml)
uv add package-name

# For dev dependencies
uv add --dev package-name
```

### Running Tests
```bash
uv run pytest
uv run pytest --cov=src tests/
```

### Code Quality
```bash
# Format code
uv run black src/ tests/

# Lint code
uv run ruff check src/ tests/

# Type check
uv run mypy src/
```

## API Endpoints

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

### Public Endpoints
- `GET /` - API information and available endpoints
- `GET /api/v1/health` - Health check
- `GET /api/v1/index` - Current Fear & Greed Index
- `GET /api/v1/history` - Historical market data
- `GET /api/v1/btc-price` - Current BTC price (Binance WebSocket)
- `GET /api/v1/prices` - All monitored asset prices (BTC, ETH, SOL)
- `GET /api/v1/stream` - Server-Sent Events for real-time updates
- `POST /api/v1/refresh` - Manually trigger data refresh

### Internal Endpoints
- `POST /api/v1/internal/cron-refresh` - Protected endpoint for Vercel Cron (requires `CRON_SECRET`)

## The Index

The Fear & Greed Index combines multiple metrics:

- **Volatility** (40%) - Market cap change percentage
- **BTC Dominance** (30%) - Bitcoin's market dominance
- **Social Sentiment** (30%) - Aggregated social signals

**Index Scale**:
- 0-20: Extreme Fear 😱
- 21-40: Fear 😰
- 41-60: Neutral 😐
- 61-80: Greed 🤑
- 81-100: Extreme Greed 🚀

## Deployment

### Vercel (Recommended)

This project includes automatic data refresh using Vercel Cron Jobs:

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Configure Environment**:
   - Set `CMC_API_KEY` with your CoinMarketCap API key
   - Set `CRON_SECRET` with a strong random secret

3. **Deploy**:
   ```bash
   vercel --prod
   ```

4. **Automatic Refresh**:
   - Data refreshes every 5 minutes automatically via Vercel Cron
   - No manual intervention needed

📖 **Full setup guide**: See [VERCEL_CRON_SETUP.md](VERCEL_CRON_SETUP.md) for detailed instructions

### Testing Cron Locally

Before deploying, test the cron endpoint:

```bash
# Add CRON_SECRET to .env
echo "CRON_SECRET=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" >> .env

# Start the server
python run_server.py

# Run tests
python test_cron.py
```

## Contributing

See [CLAUDE.md](CLAUDE.md) for development rules and guidelines.

## License

MIT
