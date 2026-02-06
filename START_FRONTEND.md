# Quick Start Guide - Fear & Greed Index Frontend

## 🚀 Step 1: Start the Backend

First, ensure your backend API is running:

```bash
# In the root project directory
python run_server.py
```

Or with uvicorn directly:

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

The backend should be accessible at: http://localhost:8000

## 🎨 Step 2: Start the Frontend

Open a new terminal and run:

```bash
cd frontend
npm run dev
```

The frontend will start at: http://localhost:5173

## ✅ Verification

1. **Backend Health Check**: Visit http://localhost:8000/api/v1/health
   - Should return: `{"status": "healthy", ...}`

2. **Frontend**: Open http://localhost:5173
   - You should see the Fear & Greed Index dashboard
   - Click the "Refresh Data" button to fetch live data

3. **CORS**: Already configured! The backend has CORS enabled with `allow_origins=["*"]`

## 🔧 Troubleshooting

### Backend not starting?
- Check if you have a valid CoinMarketCap API key in `.env`
- Run `python check_env.py` to verify your configuration

### Frontend can't connect to backend?
- Verify backend is running on port 8000
- Check `.env` file in frontend directory has: `VITE_API_BASE_URL=http://localhost:8000`
- Check browser console (F12) for error details

### Port already in use?
- **Backend**: Change port with `--port 8001`
- **Frontend**: Vite will auto-detect and use next available port (5174, etc.)

## 📱 Features to Test

1. **Main Gauge**: Shows real-time Fear & Greed score (0-100)
2. **History Chart**: Displays 7-day trends for BTC Dominance, Market Cap, and 24h Change
3. **Component Cards**: Shows breakdown of Volatility, Dominance, and Social scores
4. **Refresh Button**: Triggers backend data refresh from CoinMarketCap API
5. **Auto-refresh**: Dashboard updates every 5 minutes automatically

## 🎯 API Endpoints Used

- `GET /api/v1/index` - Current Fear & Greed Index
- `GET /api/v1/history?days=7` - Historical market data
- `POST /api/v1/refresh` - Trigger data refresh
- `GET /api/v1/health` - Health check

Enjoy your crypto sentiment dashboard! 🚀📈
