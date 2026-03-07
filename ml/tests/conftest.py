"""Pytest configuration for ML test suite."""
import sys
from pathlib import Path

# Add ml/ root to Python path so `from config import settings` etc work
ml_root = Path(__file__).parent.parent
if str(ml_root) not in sys.path:
    sys.path.insert(0, str(ml_root))
