"""
Vercel entry point for Fear & Greed Index 6900 FastAPI application.
"""
import sys
from pathlib import Path

# Add the project root to Python path to enable imports
sys.path.insert(0, str(Path(__file__).parent))

# Import the FastAPI app
from src.api.main import app

# Export for Vercel
__all__ = ["app"]
