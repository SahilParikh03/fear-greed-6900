# 🚀 Fear & Greed Index 6900 - Startup Guide

## Quick Start

### Option 1: Using Batch Scripts (Windows)

1. **Start Backend** (Terminal 1):
   ```
   Double-click: start-backend.bat
   ```
   OR manually:
   ```bash
   uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Frontend** (Terminal 2):
   ```
   Double-click: start-frontend.bat
   ```
   OR manually:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open Browser**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000/docs

---

## What's Running?

### Backend (Port 8000)
- ✅ FastAPI server with CORS enabled
- ✅ Binance WebSocket (real-time BTC/USDT prices)
- ✅ Volatility detector (±$500 in 10-minute windows)
- ✅ Server-Sent Events (SSE) for live frontend updates
- ✅ CoinMarketCap data integration

### Frontend (Port 5173)
- ✅ Vite + React + TypeScript
- ✅ Liquid Glass UI with Tailwind CSS
- ✅ Framer Motion animations
- ✅ Real-time price updates via SSE
- ✅ Dynamic Island notifications for volatility spikes

---

## Features Implemented

### 🎨 UI/UX Enhancements
- **Liquid Glass Theme**: Glassmorphism with `backdrop-blur-md` and subtle borders
- **SF Pro Display / Inter Typography**: High-contrast font weights for premium feel
- **Animated SVG Gauge**: Spring-animated needle with dynamic glow effects
- **Odometer Numbers**: Smooth rolling number transitions
- **Dynamic Island**: Apple-style expandable notifications for volatility alerts

### ⚡ Real-time Integration
- **Binance WebSocket**: Live BTC/USDT price streaming
- **Volatility Detection**: Automatic alerts for ±$500 price movements
- **Server-Sent Events**: Push notifications from backend to frontend
- **Auto-reconnection**: Resilient WebSocket connection handling

---

## Environment Variables

Create a `.env` file in the root directory:

```env
# CoinMarketCap API Key (Required for market data)
CMC_API_KEY=your_coinmarketcap_api_key_here

# Optional Settings
LOG_LEVEL=INFO
```

---

## API Endpoints

### REST Endpoints
- `GET /` - API information
- `GET /api/v1/index` - Current Fear & Greed Index
- `GET /api/v1/history?days=7` - Historical market data
- `POST /api/v1/refresh` - Trigger data refresh
- `GET /api/v1/btc-price` - Current BTC price from Binance
- `GET /api/v1/health` - Health check

### Real-time Endpoint
- `GET /api/v1/stream` - Server-Sent Events (SSE) for live updates
  - Event: `price` - BTC price updates
  - Event: `volatility` - Volatility spike alerts

---

## Troubleshooting

### Backend Won't Start
1. Check Python virtual environment: `uv sync`
2. Verify CMC API key is set in `.env`
3. Check port 8000 is available

### Frontend Won't Start
1. Install dependencies: `cd frontend && npm install`
2. Check port 5173 is available
3. Verify Node.js version: `node --version` (requires 18+)

### No Real-time Updates
1. Check backend is running on port 8000
2. Verify SSE connection in browser DevTools (Network tab)
3. Check CORS settings in backend

### Binance WebSocket Not Connecting
1. Check internet connection
2. Verify firewall isn't blocking WebSocket
3. Check backend logs for connection errors

---

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **uvicorn** - ASGI server
- **websockets** - Binance WebSocket connection
- **python-binance** - Binance API client
- **httpx** - Async HTTP client for CMC

### Frontend
- **Vite** - Lightning-fast build tool
- **React 19** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Animation library
- **Recharts** - Charting library
- **Lucide React** - Icon library

---

## Performance Notes

- **Backend**: Auto-reconnects to Binance on disconnect
- **Frontend**: SSE reconnects automatically on error
- **Rate Limits**: CMC free tier = 30 calls/minute
- **Volatility Detection**: 10-minute rolling window, ±$500 threshold

---

## Next Steps

1. ✅ Run backend: Terminal 1
2. ✅ Run frontend: Terminal 2
3. ✅ Open http://localhost:5173
4. ✅ Watch for volatility alerts! 🚨

---

**Built with 💙 by Senior Software Engineer @ Apple**
