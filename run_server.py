"""
Convenience script to start the Fear & Greed Index API server.

Usage:
    python run_server.py

Or with custom host/port:
    python run_server.py --host 127.0.0.1 --port 8080
"""

import argparse
import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Start the Fear & Greed Index API server")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )

    args = parser.parse_args()

    print(f"""
╔═══════════════════════════════════════════════════════╗
║     Fear & Greed Index 6900 - API Server              ║
╚═══════════════════════════════════════════════════════╝

Starting server on http://{args.host}:{args.port}

API Endpoints:
  → Root:          http://{args.host}:{args.port}/
  → Index:         http://{args.host}:{args.port}/api/v1/index
  → History:       http://{args.host}:{args.port}/api/v1/history
  → Refresh Data:  http://{args.host}:{args.port}/api/v1/refresh (POST)
  → Health Check:  http://{args.host}:{args.port}/api/v1/health

Interactive API docs:
  → Swagger UI:    http://{args.host}:{args.port}/docs
  → ReDoc:         http://{args.host}:{args.port}/redoc

Press CTRL+C to stop the server
""")

    uvicorn.run(
        "src.api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )


if __name__ == "__main__":
    main()
