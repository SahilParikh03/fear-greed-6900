# Fear & Greed Index 6900

## Project Vision
Build a modular, custom Crypto Fear & Greed Index using CoinMarketCap API data and advanced sentiment features. This index will provide a more nuanced view of crypto market sentiment by combining multiple data sources and custom algorithms.

## Tech Stack
- **Language**: Python 3.11+
- **API Framework**: FastAPI
- **Package Manager**: uv
- **Data Processing**: pandas, numpy
- **HTTP Client**: httpx
- **Environment**: python-dotenv

## The Rules

### Development Guidelines
1. **Always use `uv add` for adding dependencies** - Never manually edit pyproject.toml
2. **Create tests for every fetcher** - Each data fetcher must have corresponding unit tests
3. **Modular architecture** - Keep fetchers, normalizers, and aggregators in separate modules
4. **Type hints everywhere** - Use Python type annotations for all functions
5. **Error handling** - All API calls must have proper error handling and retries
6. **Documentation** - Every module needs a docstring explaining its purpose
7. **Configuration over hardcoding** - Use environment variables and config files
8. **Logging, not print statements** - Use proper logging for all output
9. **API rate limiting** - Respect CMC API rate limits (30 calls/minute on free tier)
10. **Data caching** - Cache API responses appropriately to reduce API calls

### Code Organization
- `src/fetchers/` - All data fetchers (CMC, social, etc.)
- `src/normalizers/` - Data normalization and scoring logic
- `src/aggregator/` - The "brain" that combines all signals
- `src/api/` - FastAPI routes and endpoints
- `src/utils/` - Shared utilities and helpers
- `tests/` - All test files mirroring src structure

### Commit Standards
- Keep commits atomic and focused
- Use conventional commit messages (feat:, fix:, docs:, refactor:, test:)

## Architecture Principles
- **Separation of Concerns**: Each component has one responsibility
- **Dependency Injection**: Pass dependencies explicitly
- **Fail Gracefully**: System should work even if some data sources fail
- **Observable**: Log metrics and errors for debugging
