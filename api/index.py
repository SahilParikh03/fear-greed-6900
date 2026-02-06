"""
Vercel serverless function entry point for FastAPI application.

This module serves as the entry point for Vercel's serverless function deployment,
exposing the FastAPI app from src.api.main.
"""

from src.api.main import app

# Vercel expects the ASGI app to be named 'app'
__all__ = ["app"]
