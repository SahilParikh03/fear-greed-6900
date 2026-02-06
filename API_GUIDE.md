# Fear & Greed Index 6900 - API Guide

## Quick Start

### 1. Start the Server

```bash
# Using the convenience script
python run_server.py

# Or with uv
uv run python run_server.py

# With auto-reload for development
python run_server.py --reload

# Custom host and port
python run_server.py --host 0.0.0.0 --port 8080
```

The server will start at `http://127.0.0.1:8000` by default.

### 2. Access the API Documentation

Once the server is running, visit:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### 3. Test the API

```bash
# Run the test script (in a new terminal while server is running)
python test_api.py
```

## API Endpoints

### GET `/`
Root endpoint with API information.

**Response:**
```json
{
  "name": "Fear & Greed Index 6900",
  "version": "1.0.0",
  "endpoints": {
    "index": "/api/v1/index",
    "history": "/api/v1/history",
    "refresh": "/api/v1/refresh",
    "health": "/api/v1/health"
  }
}
```

### GET `/api/v1/index`
Get the current Fear & Greed Index with full breakdown.

**Response:**
```json
{
  "master_score": 65.23,
  "sentiment": "GREED",
  "breakdown": {
    "volatility": 72.5,
    "dominance": 58.3,
    "social": 50.0
  },
  "component_details": {
    "volatility": {
      "score": 72.5,
      "signal": "greed",
      "reasoning": "Market cap growing (3.45%) indicates buying pressure"
    },
    "dominance": {
      "score": 58.3,
      "signal": "neutral",
      "reasoning": "BTC dominance (48.5%) in neutral range"
    },
    "social": {
      "score": 50.0,
      "signal": "neutral",
      "reasoning": "Mock/Config: Neutral social sentiment (default)"
    }
  },
  "weights": {
    "volatility": 0.4,
    "dominance": 0.3,
    "social": 0.3
  },
  "timestamp": "2026-02-05T21:30:00"
}
```

**Sentiment Labels:**
- `0-24`: EXTREME FEAR
- `25-44`: FEAR
- `45-55`: NEUTRAL
- `56-75`: GREED
- `76-100`: EXTREME GREED

### GET `/api/v1/history?days=7`
Get historical market data snapshots.

**Query Parameters:**
- `days` (optional): Number of days to retrieve (default: 7)

**Response:**
```json
{
  "count": 7,
  "data": [
    {
      "timestamp": "2026-02-05T20:00:00",
      "total_market_cap": 2500000000000,
      "btc_dominance": 48.5,
      "total_volume_24h": 150000000000,
      "market_cap_change_24h": 3.45
    },
    ...
  ]
}
```

### POST `/api/v1/refresh`
Trigger a data refresh from CoinMarketCap API.

**Response:**
```json
{
  "status": "accepted",
  "message": "Data refresh initiated in background",
  "timestamp": "2026-02-05T21:30:00"
}
```

**Notes:**
- This runs as a background task
- New data will be available within a few seconds
- Respects API rate limits (30 calls/minute)

### GET `/api/v1/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-05T21:30:00",
  "components": {
    "api": "operational",
    "history_manager": "operational",
    "record_count": 42
  }
}
```

## Architecture

### Components

```
┌─────────────────────────────────────────────┐
│           FastAPI Application               │
│            (src/api/main.py)                │
└──────────────┬──────────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌─────────────┐  ┌─────────────┐
│  CMCFetcher │  │   Master    │
│  (Data In)  │  │ Aggregator  │
└──────┬──────┘  └──────┬──────┘
       │                │
       ▼                ▼
┌─────────────┐  ┌─────────────┐
│   History   │  │   Scorers   │
│   Manager   │  │  - Volatility│
└─────────────┘  │  - Dominance│
                 │  - Social   │
                 └─────────────┘
```

### Data Flow

1. **Fetch**: CMCFetcher retrieves data from CoinMarketCap API
2. **Persist**: HistoryManager saves snapshots to CSV
3. **Score**: Individual scorers calculate component scores
4. **Aggregate**: MasterAggregator combines scores with weights
5. **Serve**: FastAPI exposes results via REST endpoints

## Weights Configuration

The current weighting scheme (configurable in `src/api/main.py`):

- **Volatility: 40%** - Market behavior is the strongest signal
- **BTC Dominance: 30%** - Flight to safety vs. speculation
- **Social Sentiment: 30%** - Future expansion (currently mock data)

To modify weights, edit the `MasterAggregator` initialization:

```python
master_aggregator = MasterAggregator(
    volatility_weight=0.40,  # Change this
    dominance_weight=0.30,   # Change this
    social_weight=0.30       # Change this (must sum to 1.0)
)
```

## Background Worker

The API uses FastAPI's `BackgroundTasks` for the `/api/v1/refresh` endpoint. This:

1. Accepts the POST request immediately
2. Runs the CMC data fetch in the background
3. Updates the history file asynchronously
4. Allows the API to remain responsive

### Alternative: Scheduled Updates

For production, consider using a task scheduler like:

- **APScheduler** for in-process scheduling
- **Celery** for distributed task queues
- **Cron jobs** calling `/api/v1/refresh`

Example with APScheduler (add to `main.py`):

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

@app.on_event("startup")
async def startup_event():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(refresh_data_task, 'interval', hours=1)
    scheduler.start()
```

## Testing in Browser

Once the server is running, you can test directly in your browser:

1. **Get Current Index**: http://127.0.0.1:8000/api/v1/index
2. **View History**: http://127.0.0.1:8000/api/v1/history?days=7
3. **Health Check**: http://127.0.0.1:8000/api/v1/health

For POST requests (like `/api/v1/refresh`), use the Swagger UI at http://127.0.0.1:8000/docs

## Error Handling

The API handles errors gracefully:

- **No data available**: Returns 500 with message to run `/api/v1/refresh`
- **CMC API errors**: Logged and propagated with details
- **Rate limiting**: Automatic backoff and retry
- **Missing components**: Scores calculated with available data

## Next Steps

### Immediate
- [ ] Run initial data refresh: `curl -X POST http://127.0.0.1:8000/api/v1/refresh`
- [ ] Test the index endpoint
- [ ] View the interactive API docs

### Future Enhancements
- [ ] Implement real social sentiment (Twitter, Reddit)
- [ ] Add scheduled background updates
- [ ] Create a frontend dashboard
- [ ] Add more data sources (on-chain metrics, derivatives data)
- [ ] Implement caching layer (Redis)
- [ ] Add authentication for write operations
