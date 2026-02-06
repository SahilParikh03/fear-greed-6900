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

- `GET /health` - Health check
- `GET /api/v1/index` - Current Fear & Greed Index
- `GET /api/v1/metrics` - Detailed metric breakdown
- `GET /api/v1/history` - Historical index values

## The Index

The Fear & Greed Index combines multiple metrics:

- **Volatility** (25%) - High volatility = Fear
- **Volume** (20%) - High volume = Greed
- **BTC Dominance** (20%) - High dominance = Fear
- **Social Sentiment** (20%) - Positive sentiment = Greed
- **Altcoin Season** (15%) - Alts outperforming = Greed

**Index Scale**:
- 0-20: Extreme Fear 😱
- 21-40: Fear 😰
- 41-60: Neutral 😐
- 61-80: Greed 🤑
- 81-100: Extreme Greed 🚀

## Contributing

See [CLAUDE.md](CLAUDE.md) for development rules and guidelines.

## License

MIT
