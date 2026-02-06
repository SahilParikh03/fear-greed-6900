# Vercel Deployment Guide

## Issue Fixed: Read-Only File System Error

The application has been updated to work on Vercel's serverless platform, which has a read-only file system except for `/tmp`.

### Changes Made

1. **HistoryManager Update** (`src/utils/history_manager.py`)
   - Automatically detects serverless environments (Vercel, AWS Lambda, Google Cloud Functions)
   - Uses `/tmp` directory for storage on serverless platforms
   - Uses local `data/` directory for development
   - Graceful error handling if directory creation fails

2. **Startup Warnings** (`src/api/main.py`)
   - Added warning messages about ephemeral storage on Vercel
   - Health check now shows storage mode (ephemeral vs persistent)

### Important Limitations on Vercel

⚠️ **Ephemeral Storage**: The `/tmp` directory on Vercel is cleared between function invocations. This means:

- Historical data will NOT persist between deployments
- Trends and historical analysis will be limited
- Each cold start creates a fresh history file

### Recommended Solutions for Production

For production deployments, consider using persistent storage:

1. **Database Options**
   - PostgreSQL (Vercel Postgres)
   - MongoDB Atlas
   - Supabase

2. **Cloud Storage**
   - AWS S3
   - Google Cloud Storage
   - Azure Blob Storage

3. **Managed Services**
   - Redis (Upstash Redis)
   - Firebase Realtime Database

### Environment Variables Required

Make sure these are set in your Vercel project settings:

```bash
CMC_API_KEY=your_coinmarketcap_api_key
CRON_SECRET=your_secret_for_cron_endpoint
```

### Testing the Deployment

After deploying to Vercel:

1. Check the health endpoint: `https://your-app.vercel.app/api/v1/health`
2. Trigger a data refresh: `POST https://your-app.vercel.app/api/v1/refresh`
3. Get the index: `https://your-app.vercel.app/api/v1/index`

### Local Development

For local development, the app will use `data/processed/market_history.csv` for persistent storage as before.

Run locally with:
```bash
uv run uvicorn src.api.main:app --reload
```
