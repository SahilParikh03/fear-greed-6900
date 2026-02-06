# Fear & Greed Index 6900 - Architecture

## Overview
The system follows a pipeline architecture with clear data flow from multiple sources through normalization to final aggregation.

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                             │
├─────────────────────────────────────────────────────────────┤
│  CMC API  │  Social APIs  │  On-Chain Data  │  Historical   │
└─────┬───────────┬─────────────┬─────────────────┬───────────┘
      │           │             │                 │
      ▼           ▼             ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│                       FETCHERS                               │
├─────────────────────────────────────────────────────────────┤
│  - CMCFetcher: Get market data (vol, dominance, volume)     │
│  - SocialFetcher: Get sentiment from social platforms       │
│  - AltcoinFetcher: Track altcoin performance vs BTC         │
│  - Each fetcher implements BaseFetcher interface            │
│  - Built-in rate limiting, retry logic, caching             │
└─────┬───────────────────────────────────────────────────────┘
      │
      │ Raw Data (JSON/Dicts)
      ▼
┌─────────────────────────────────────────────────────────────┐
│                    NORMALIZERS                               │
├─────────────────────────────────────────────────────────────┤
│  - VolatilityNormalizer: 0-100 scale (high vol = fear)      │
│  - VolumeNormalizer: 0-100 scale (high vol = greed)         │
│  - DominanceNormalizer: 0-100 scale (high dom = fear)       │
│  - SentimentNormalizer: 0-100 scale from text analysis      │
│  - AltcoinSeasonNormalizer: 0-100 based on alt performance  │
│  - Uses Min-Max scaling with historical baselines           │
│  - Outputs standardized scores (0 = extreme fear, 100 = extreme greed) │
└─────┬───────────────────────────────────────────────────────┘
      │
      │ Normalized Scores (0-100)
      ▼
┌─────────────────────────────────────────────────────────────┐
│                  AGGREGATOR (Brain)                          │
├─────────────────────────────────────────────────────────────┤
│  - Collects all normalized metrics                          │
│  - Applies configurable weights to each metric              │
│  - Calculates weighted average                              │
│  - Default weights:                                          │
│    * Volatility: 25%                                         │
│    * Volume: 20%                                             │
│    * BTC Dominance: 20%                                      │
│    * Social Sentiment: 20%                                   │
│    * Altcoin Season: 15%                                     │
│  - Outputs final Fear & Greed Index (0-100)                 │
│  - Classifies result:                                        │
│    * 0-20: Extreme Fear                                      │
│    * 21-40: Fear                                             │
│    * 41-60: Neutral                                          │
│    * 61-80: Greed                                            │
│    * 81-100: Extreme Greed                                   │
└─────┬───────────────────────────────────────────────────────┘
      │
      │ Final Index + Breakdown
      ▼
┌─────────────────────────────────────────────────────────────┐
│                    FASTAPI SERVER                            │
├─────────────────────────────────────────────────────────────┤
│  Endpoints:                                                  │
│  - GET /health          - Health check                       │
│  - GET /api/v1/index    - Current index value + label        │
│  - GET /api/v1/metrics  - Full breakdown of all metrics      │
│  - GET /api/v1/history  - Historical index values            │
│  - Implements caching to reduce API calls                    │
│  - Returns JSON responses                                    │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Fetchers (`src/fetchers/`)
**Purpose**: Retrieve raw data from external sources

**Interface**:
```python
class BaseFetcher(ABC):
    @abstractmethod
    async def fetch(self) -> dict:
        """Fetch raw data from source"""
        pass
```

**Responsibilities**:
- API authentication
- Rate limiting
- Error handling and retries
- Data validation
- Caching responses

### 2. Normalizers (`src/normalizers/`)
**Purpose**: Convert raw data into standardized 0-100 scores

**Interface**:
```python
class BaseNormalizer(ABC):
    @abstractmethod
    def normalize(self, raw_data: dict) -> float:
        """Convert raw data to 0-100 scale"""
        pass
```

**Responsibilities**:
- Min-Max scaling using historical data
- Z-score calculations
- Handling missing data
- Maintaining historical baselines

### 3. Aggregator (`src/aggregator/`)
**Purpose**: Combine all metrics into final index

**Responsibilities**:
- Apply configurable weights
- Calculate weighted average
- Classify result into fear/greed categories
- Handle missing metrics gracefully
- Provide detailed breakdown

### 4. API Layer (`src/api/`)
**Purpose**: Expose index via REST API

**Responsibilities**:
- Route handling
- Request validation
- Response formatting
- Error responses
- CORS configuration
- API documentation

## Configuration

All components are configurable via:
- Environment variables (`.env`)
- Config file (`config/settings.yaml`)
- Runtime parameters

## Error Handling Strategy

1. **Fetcher Fails**: Return None, log error, continue with available data
2. **Normalizer Fails**: Use default/neutral score (50)
3. **All Metrics Fail**: Return error response from API
4. **Partial Data**: Calculate index with available metrics, flag as incomplete

## Data Storage

- **Cache**: In-memory (Redis optional for production)
- **Historical Data**: SQLite for development, PostgreSQL for production
- **Retention**: 90 days of historical scores

## Performance Considerations

- All fetchers run asynchronously
- Responses cached for 5 minutes
- Historical data cached for 1 hour
- Rate limiting on all external API calls

## Extensibility

New metrics can be added by:
1. Creating a new Fetcher (implements `BaseFetcher`)
2. Creating a new Normalizer (implements `BaseNormalizer`)
3. Registering in Aggregator with weight
4. No changes needed to API layer
