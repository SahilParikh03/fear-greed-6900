# Vercel Cron Automation Setup

This guide explains how to set up automatic data refresh using Vercel's Cron Jobs feature.

## Overview

The Fear & Greed Index 6900 uses Vercel Cron to automatically refresh market data every 5 minutes without manual intervention. This ensures the index always reflects the latest market conditions.

## How It Works

1. **Vercel Cron** triggers the `/api/v1/internal/cron-refresh` endpoint every 5 minutes
2. The endpoint verifies the request using a secret token for security
3. Market data is fetched from CoinMarketCap and saved to history
4. The index is updated with fresh data

## Configuration

### 1. Set Up Environment Variables

Add the following to your Vercel project's environment variables:

```bash
CRON_SECRET=<generate-a-strong-random-secret>
```

**Important:** Use a strong, random secret! You can generate one with:

```bash
# Linux/Mac
openssl rand -base64 32

# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Add to Vercel Project Settings

1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Add `CRON_SECRET` with your generated secret value
4. Make sure it's available for all environments (Production, Preview, Development)

### 3. Deploy to Vercel

The `vercel.json` file is already configured with the cron schedule:

```json
{
  "crons": [
    {
      "path": "/api/v1/internal/cron-refresh",
      "schedule": "*/5 * * * *"
    }
  ]
}
```

Simply deploy your project:

```bash
vercel --prod
```

## Cron Schedule

**Current Schedule:** `*/5 * * * *` (Every 5 minutes)

### Common Cron Patterns

You can modify the schedule in `vercel.json`:

- `*/5 * * * *` - Every 5 minutes
- `*/10 * * * *` - Every 10 minutes
- `*/15 * * * *` - Every 15 minutes
- `0 * * * *` - Every hour (at minute 0)
- `0 */2 * * *` - Every 2 hours
- `0 0 * * *` - Once daily at midnight

## Security

### How the Endpoint is Protected

1. **Authorization Header**: Vercel Cron automatically includes an `Authorization` header with the `CRON_SECRET` value
2. **Constant-Time Comparison**: Uses `secrets.compare_digest()` to prevent timing attacks
3. **Logging**: Failed authentication attempts are logged with client IP
4. **Environment Variable**: Secret is stored securely in Vercel's environment

### Testing the Endpoint

To test the cron endpoint locally:

```bash
# Set CRON_SECRET in your .env file
echo "CRON_SECRET=test-secret-123" >> .env

# Make a test request
curl -X POST http://localhost:8000/api/v1/internal/cron-refresh \
  -H "Authorization: test-secret-123"
```

Expected response:

```json
{
  "status": "accepted",
  "message": "Cron-triggered data refresh initiated in background",
  "timestamp": "2026-02-06T12:00:00"
}
```

### Security Best Practices

✅ **DO:**
- Use a strong, random secret (32+ characters)
- Store `CRON_SECRET` only in Vercel environment variables
- Never commit the secret to version control
- Rotate the secret periodically

❌ **DON'T:**
- Use simple or guessable secrets
- Share the secret in documentation or commits
- Expose the endpoint publicly without protection
- Reuse secrets across different projects

## Monitoring

### Check Cron Status

View cron job execution in your Vercel dashboard:

1. Go to **Deployments** → Select your deployment
2. Click on **Functions** → **Cron Jobs**
3. View execution history and logs

### Health Check

Verify the cron is working:

```bash
curl https://your-app.vercel.app/api/v1/health
```

Check the `record_count` to see if data is being updated.

### Logs

View detailed logs in Vercel:

```bash
vercel logs <deployment-url>
```

Look for entries like:
```
INFO - Cron job triggered: refreshing market data
INFO - Data refresh completed successfully
```

## Troubleshooting

### Cron Not Triggering

1. **Check Environment Variables**: Ensure `CRON_SECRET` is set in Vercel
2. **Verify Deployment**: Make sure you deployed to production (`vercel --prod`)
3. **Check Logs**: Look for errors in Vercel logs
4. **Validate Schedule**: Confirm `vercel.json` has correct cron syntax

### 401 Unauthorized

- The `Authorization` header is missing or empty
- Check that Vercel Cron is properly configured

### 403 Forbidden

- The `CRON_SECRET` in Vercel doesn't match the one in your endpoint
- Ensure environment variables are deployed correctly

### 500 Internal Server Error

- `CRON_SECRET` environment variable is not set
- Add it to your Vercel project settings

## API Rate Limits

**CoinMarketCap Free Tier:** 30 calls/minute

With a 5-minute cron schedule:
- **Calls per hour:** 12
- **Daily usage:** ~288 calls
- **Monthly usage:** ~8,640 calls

This is well within the free tier limit (10,000 calls/month).

### Adjusting for Rate Limits

If you upgrade to a paid plan, you can reduce the interval:

```json
{
  "schedule": "*/1 * * * *"  // Every minute (requires higher tier)
}
```

## Cost

**Vercel Cron Jobs:**
- ✅ Free on all Vercel plans (Hobby, Pro, Enterprise)
- No additional charges for cron execution

**CoinMarketCap API:**
- ✅ Free tier: 10,000 calls/month
- 💰 Paid tiers available for higher limits

## Further Reading

- [Vercel Cron Jobs Documentation](https://vercel.com/docs/cron-jobs)
- [Cron Expression Generator](https://crontab.guru/)
- [CoinMarketCap API Documentation](https://coinmarketcap.com/api/documentation/v1/)
