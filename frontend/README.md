# Fear & Greed Index 6900 - Frontend

A modern, dark-mode crypto dashboard built with React, TypeScript, and Tailwind CSS.

## Features

- **Real-time Sentiment Gauge**: Visual gauge showing the current Fear & Greed score
- **Historical Charts**: Interactive line charts displaying 7-day market history
- **Component Breakdown**: Detailed cards for Volatility, BTC Dominance, and Social Sentiment
- **Auto-refresh**: Automatically updates every 5 minutes
- **Manual Refresh**: Button to trigger on-demand data refresh
- **Dark Mode**: Beautiful crypto-themed dark interface
- **Responsive Design**: Works on desktop, tablet, and mobile

## Tech Stack

- **React 18** with TypeScript
- **Vite** for blazing-fast development
- **Tailwind CSS** for styling
- **Recharts** for data visualization
- **Axios** for API calls
- **Lucide React** for icons

## Prerequisites

- Node.js 18+ or npm
- Backend API running on http://localhost:8000

## Installation

```bash
npm install
```

## Configuration

The frontend connects to the backend API. By default, it uses http://localhost:8000.

To change the API URL, edit the .env file:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Development

Start the development server:

```bash
npm run dev
```

The app will be available at http://localhost:5173

## Building for Production

Build the optimized production bundle:

```bash
npm run build
```

Preview the production build:

```bash
npm run preview
```

## CORS Configuration

The backend already has CORS enabled, so the frontend can connect from any origin. No additional CORS configuration is needed.

## Troubleshooting

### "Failed to fetch data" error

1. Make sure the backend is running
2. Verify the backend is accessible at http://localhost:8000
3. Check the browser console for detailed error messages

### Port conflicts

If port 5173 is in use, Vite will automatically try the next available port.
