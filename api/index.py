"""Vercel Python serverless entrypoint. Forwards to the FastAPI ASGI app."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.main import app  # noqa
