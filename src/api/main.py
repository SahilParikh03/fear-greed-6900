"""
FastAPI application for the Fear & Greed Index 6900.

This module provides REST API endpoints for accessing the Fear & Greed Index,
historical data, and triggering data refresh operations.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from collections import deque

from fastapi import FastAPI, HTTPException, BackgroundTasks, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.fetchers.cmc_fetcher import CMCFetcher
from src.normalizers.market_scorers import DominanceScorer, VolatilityScorer
from src.normalizers.social_scorer import SocialSentimentScorer
from src.aggregator.brain import MasterAggregator
from src.utils.history_manager import HistoryManager
from src.services.binance_ws import get_binance_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Fear & Greed Index 6900",
    description="Custom Crypto Fear & Greed Index using CoinMarketCap data",
    version="1.0.0"
)

# Add CORS middleware for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
history_manager = HistoryManager()
dominance_scorer = DominanceScorer()
volatility_scorer = VolatilityScorer()
social_scorer = SocialSentimentScorer()
master_aggregator = MasterAggregator(
    volatility_weight=0.40,
    dominance_weight=0.30,
    social_weight=0.30
)

# Initialize Binance WebSocket service
binance_service = get_binance_service()

# Event queues for SSE
price_event_queue: deque = deque(maxlen=100)
volatility_event_queue: deque = deque(maxlen=50)
crash_event_queue: deque = deque(maxlen=50)  # New: for VOLATILITY_CRASH events


# Pydantic models for API responses
class ComponentScore(BaseModel):
    """Individual component score details."""
    score: float
    signal: str
    reasoning: str


class IndexResponse(BaseModel):
    """Response model for the Fear & Greed Index."""
    master_score: float
    sentiment: str
    breakdown: Dict[str, float]
    component_details: Dict[str, ComponentScore]
    weights: Dict[str, float]
    timestamp: str


class HistoryItem(BaseModel):
    """Historical data point."""
    timestamp: str
    total_market_cap: float
    btc_dominance: float
    total_volume_24h: Optional[float] = None
    market_cap_change_24h: Optional[float] = None


class HistoryResponse(BaseModel):
    """Response model for historical data."""
    count: int
    data: List[HistoryItem]


class RefreshResponse(BaseModel):
    """Response model for refresh operations."""
    status: str
    message: str
    timestamp: str


class BTCPriceResponse(BaseModel):
    """Response model for BTC price."""
    price: Optional[float]
    timestamp: str
    source: str


class AgentSignalResponse(BaseModel):
    """Response model for agent decision signal."""
    index_score: float
    sentiment: str
    recommendation: str
    is_volatile: bool
    timestamp: str


def get_recommendation(score: float) -> str:
    """
    Determine trading recommendation based on Fear & Greed score.

    Args:
        score: The Fear & Greed Index score (0-100)

    Returns:
        Recommendation string for agent decision-making
    """
    if score < 20:
        return "STRONG_BUY"
    elif score < 35:
        return "ACCUMULATE_BTC"
    elif score < 45:
        return "BUY_DIP"
    elif score < 55:
        return "HOLD"
    elif score < 70:
        return "TAKE_SOME_PROFIT"
    elif score < 80:
        return "REDUCE_POSITION"
    else:
        return "TAKE_PROFIT"


async def calculate_current_index() -> Dict:
    """
    Calculate the current Fear & Greed Index from latest data.

    Returns:
        Dictionary containing master score, sentiment, and breakdown
    """
    try:
        # Get latest historical data
        latest = history_manager.get_latest()

        if not latest:
            raise ValueError("No historical data available. Please run /api/v1/refresh first.")

        # Calculate volatility score
        market_cap_change = latest.get("market_cap_change_24h")
        if market_cap_change is None:
            logger.warning("No market cap change data available, using 0%")
            market_cap_change = 0.0

        volatility_result = volatility_scorer.score(market_cap_change)

        # Calculate dominance score
        btc_dominance = latest.get("btc_dominance")
        if btc_dominance is None:
            raise ValueError("BTC dominance data not available")

        dominance_result = dominance_scorer.score(btc_dominance)

        # Get social sentiment score
        social_result = social_scorer.get_combined_social_score()

        # Calculate master score
        master_result = master_aggregator.calculate_master_score(
            volatility_score=volatility_result["score"],
            dominance_score=dominance_result["score"],
            social_score=social_result["score"]
        )

        logger.info(
            f"Index calculated: {master_result['score']:.2f} ({master_result['label']})"
        )

        return {
            "master_score": master_result["score"],
            "sentiment": master_result["label"],
            "breakdown": master_result["components"],
            "component_details": {
                "volatility": {
                    "score": volatility_result["score"],
                    "signal": volatility_result["signal"],
                    "reasoning": volatility_result["reasoning"]
                },
                "dominance": {
                    "score": dominance_result["score"],
                    "signal": dominance_result["signal"],
                    "reasoning": dominance_result["reasoning"]
                },
                "social": {
                    "score": social_result["score"],
                    "signal": social_result["signal"],
                    "reasoning": social_result["reasoning"]
                }
            },
            "weights": master_result["weights"],
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to calculate index: {e}")
        raise


async def refresh_data_task():
    """
    Background task to refresh market data from CoinMarketCap.

    Fetches latest global metrics and updates history file.
    """
    try:
        logger.info("Starting data refresh...")

        # Fetch data from CoinMarketCap
        async with CMCFetcher() as fetcher:
            data = await fetcher.fetch()

        # Extract relevant metrics
        global_data = data["global_metrics"]["data"]
        quote = global_data["quote"]["USD"]

        total_market_cap = quote["total_market_cap"]
        btc_dominance = global_data["btc_dominance"]
        total_volume_24h = quote.get("total_volume_24h")
        market_cap_change_24h = quote.get("total_market_cap_yesterday_percentage_change")

        # Save to history
        success = history_manager.save_snapshot(
            total_market_cap=total_market_cap,
            btc_dominance=btc_dominance,
            total_volume_24h=total_volume_24h,
            market_cap_change_24h=market_cap_change_24h
        )

        if success:
            logger.info("Data refresh completed successfully")
        else:
            logger.error("Failed to save data to history")

    except Exception as e:
        logger.error(f"Data refresh failed: {e}")
        raise


# WebSocket event handlers
async def on_price_update(price_data: Dict):
    """Handle price updates from Binance WebSocket."""
    price_event_queue.append(price_data)


async def on_volatility_spike(volatility_data: Dict):
    """Handle legacy volatility spike events from Binance WebSocket (BTC only)."""
    volatility_event_queue.append(volatility_data)
    logger.warning(f"Volatility spike queued: ${volatility_data['price_change']:.2f}")


async def on_volatility_crash(crash_data: Dict):
    """Handle VOLATILITY_CRASH events from Binance WebSocket (multi-asset)."""
    crash_event_queue.append(crash_data)
    logger.warning(
        f"💥 {crash_data['asset']} CRASH queued: "
        f"{crash_data['magnitude']:.2f}% drop (${crash_data['price_drop']:.2f})"
    )


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Start Binance WebSocket service on app startup."""
    logger.info("🚀 Starting Fear & Greed Index 6900...")

    # Subscribe to Binance events
    binance_service.subscribe_price(on_price_update)
    binance_service.subscribe_volatility(on_volatility_spike)
    binance_service.subscribe_crash(on_volatility_crash)  # New: subscribe to crash events

    # Start Binance WebSocket in background
    asyncio.create_task(binance_service.start())

    logger.info("✅ Binance WebSocket service started (monitoring BTC, ETH, SOL)")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop Binance WebSocket service on app shutdown."""
    logger.info("Stopping Binance WebSocket service...")
    await binance_service.stop()


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Fear & Greed Index 6900",
        "version": "1.0.0",
        "endpoints": {
            "index": "/api/v1/index",
            "agent_signal": "/api/v1/agent/signal",
            "history": "/api/v1/history",
            "refresh": "/api/v1/refresh",
            "btc_price": "/api/v1/btc-price",
            "prices": "/api/v1/prices",
            "stream": "/api/v1/stream",
            "health": "/api/v1/health"
        },
        "internal": {
            "cron_refresh": "/api/v1/internal/cron-refresh (protected)"
        }
    }


@app.get("/api/v1/index", response_model=IndexResponse)
async def get_index():
    """
    Get the current Fear & Greed Index.

    Returns the master score, sentiment label, component breakdown,
    and detailed reasoning for each component.
    """
    try:
        result = await calculate_current_index()
        return result
    except Exception as e:
        logger.error(f"Error in /api/v1/index: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/history", response_model=HistoryResponse)
async def get_history(days: int = 7):
    """
    Get historical market data.

    Args:
        days: Number of days of history to retrieve (default: 7)

    Returns:
        Historical snapshots of market data
    """
    try:
        history = history_manager.load_history(limit=days)

        return {
            "count": len(history),
            "data": history
        }
    except Exception as e:
        logger.error(f"Error in /api/v1/history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/refresh", response_model=RefreshResponse)
async def refresh_data(background_tasks: BackgroundTasks):
    """
    Trigger a refresh of market data from CoinMarketCap.

    This endpoint triggers a background task to fetch fresh data
    and update the history file.
    """
    try:
        # Run refresh in background
        background_tasks.add_task(refresh_data_task)

        return {
            "status": "accepted",
            "message": "Data refresh initiated in background",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in /api/v1/refresh: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/internal/cron-refresh", response_model=RefreshResponse)
async def cron_refresh_data(
    background_tasks: BackgroundTasks,
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """
    Internal endpoint for Vercel Cron to refresh market data.

    This endpoint is protected by a CRON_SECRET header and should only
    be called by Vercel's cron service.

    Security:
        - Requires Authorization header matching CRON_SECRET env var
        - Vercel cron automatically adds this header
    """
    try:
        # Get the expected cron secret from environment
        expected_secret = os.getenv("CRON_SECRET")

        if not expected_secret:
            logger.error("CRON_SECRET not configured in environment")
            raise HTTPException(
                status_code=500,
                detail="Server configuration error: CRON_SECRET not set"
            )

        # Verify the authorization header
        if not authorization:
            logger.warning("Cron endpoint accessed without Authorization header")
            raise HTTPException(
                status_code=401,
                detail="Unauthorized: Missing Authorization header"
            )

        # Compare secrets (use constant-time comparison to prevent timing attacks)
        import secrets
        if not secrets.compare_digest(authorization, expected_secret):
            logger.warning(f"Cron endpoint accessed with invalid secret from {request.client.host if request.client else 'unknown'}")
            raise HTTPException(
                status_code=403,
                detail="Forbidden: Invalid credentials"
            )

        logger.info("Cron job triggered: refreshing market data")

        # Run refresh in background
        background_tasks.add_task(refresh_data_task)

        return {
            "status": "accepted",
            "message": "Cron-triggered data refresh initiated in background",
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /api/v1/internal/cron-refresh: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/btc-price", response_model=BTCPriceResponse)
async def get_btc_price():
    """
    Get current BTC price from Binance WebSocket.

    Returns the most recent BTC/USDT price.
    """
    price = binance_service.get_current_price("BTC")

    return {
        "price": price,
        "timestamp": datetime.now().isoformat(),
        "source": "Binance WebSocket"
    }


@app.get("/api/v1/prices")
async def get_all_prices():
    """
    Get current prices for all monitored assets (BTC, ETH, SOL).

    Returns prices from Binance WebSocket.
    """
    prices = binance_service.get_all_prices()

    return {
        "prices": prices,
        "timestamp": datetime.now().isoformat(),
        "source": "Binance WebSocket",
        "assets": list(prices.keys())
    }


@app.post("/api/v1/agent/signal", response_model=AgentSignalResponse)
async def get_agent_signal():
    """
    Get simplified agent decision signal.

    This endpoint provides a streamlined response optimized for AI agents
    and automated trading systems. Returns the current Fear & Greed score,
    sentiment, actionable recommendation, and volatility status.

    Recommendation logic:
    - Score < 20: STRONG_BUY (extreme fear - best buying opportunity)
    - Score 20-35: ACCUMULATE_BTC (fear - good accumulation zone)
    - Score 35-45: BUY_DIP (slight fear - wait for dips)
    - Score 45-55: HOLD (neutral - maintain positions)
    - Score 55-70: TAKE_SOME_PROFIT (greed - consider taking profits)
    - Score 70-80: REDUCE_POSITION (strong greed - reduce exposure)
    - Score > 80: TAKE_PROFIT (extreme greed - sell into strength)

    Volatility detection:
    - Checks if volatility score > 60 (high volatility)
    - Checks if market cap changed > 5% in 24h (significant move)
    - Checks for recent crash events in the queue
    """
    try:
        # Calculate current index
        index_data = await calculate_current_index()

        # Extract core metrics
        score = index_data["master_score"]
        sentiment = index_data["sentiment"]

        # Determine recommendation based on score
        recommendation = get_recommendation(score)

        # Determine volatility status
        # Check multiple signals: volatility score, market cap change, recent crashes
        volatility_score = index_data["component_details"]["volatility"]["score"]
        is_volatile = volatility_score > 60  # High volatility threshold

        # Also check if there have been recent crash events
        if len(crash_event_queue) > 0:
            is_volatile = True

        # Check market cap change from latest data
        latest = history_manager.get_latest()
        if latest and latest.get("market_cap_change_24h"):
            market_cap_change = abs(latest["market_cap_change_24h"])
            if market_cap_change > 5.0:  # More than 5% change
                is_volatile = True

        logger.info(
            f"Agent signal: score={score:.2f}, sentiment={sentiment}, "
            f"recommendation={recommendation}, volatile={is_volatile}"
        )

        return {
            "index_score": round(score, 2),
            "sentiment": sentiment,
            "recommendation": recommendation,
            "is_volatile": is_volatile,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error in /api/v1/agent/signal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/stream")
async def stream_events():
    """
    Server-Sent Events (SSE) endpoint for real-time updates.

    Streams price updates and volatility alerts to connected clients.
    """
    async def event_generator():
        """Generate SSE events from queued data."""
        last_price_index = 0
        last_volatility_index = 0
        last_crash_index = 0

        while True:
            try:
                # Send price updates
                if len(price_event_queue) > last_price_index:
                    for i in range(last_price_index, len(price_event_queue)):
                        event = price_event_queue[i]
                        yield f"event: price\ndata: {json.dumps(event)}\n\n"
                    last_price_index = len(price_event_queue)

                # Send volatility alerts (legacy BTC)
                if len(volatility_event_queue) > last_volatility_index:
                    for i in range(last_volatility_index, len(volatility_event_queue)):
                        event = volatility_event_queue[i]
                        yield f"event: volatility\ndata: {json.dumps(event)}\n\n"
                    last_volatility_index = len(volatility_event_queue)

                # Send crash alerts (multi-asset)
                if len(crash_event_queue) > last_crash_index:
                    for i in range(last_crash_index, len(crash_event_queue)):
                        event = crash_event_queue[i]
                        yield f"event: crash\ndata: {json.dumps(event)}\n\n"
                    last_crash_index = len(crash_event_queue)

                # Heartbeat to keep connection alive
                yield f": heartbeat\n\n"

                await asyncio.sleep(1)

            except asyncio.CancelledError:
                logger.info("SSE stream cancelled")
                break
            except Exception as e:
                logger.error(f"Error in SSE stream: {e}")
                break

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/api/v1/health")
async def health_check():
    """
    Health check endpoint.

    Returns the status of the API and its dependencies.
    """
    try:
        # Check if history file exists and has data
        history_stats = history_manager.get_stats()
        has_data = history_stats.get("record_count", 0) > 0

        # Check Binance connection and get all asset prices
        all_prices = binance_service.get_all_prices()
        binance_status = "connected" if any(all_prices.values()) else "disconnected"

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "api": "operational",
                "history_manager": "operational" if has_data else "no_data",
                "binance_websocket": binance_status,
                "record_count": history_stats.get("record_count", 0),
                "current_prices": all_prices
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
