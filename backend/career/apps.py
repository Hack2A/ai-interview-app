import sys
from pathlib import Path
from django.apps import AppConfig

# Global orchestrator instance for local reuse (lazy-loaded singleton)
_orchestrator = None


def _ensure_ml_path():
    """Add the ml/ directory to sys.path so we can import orchestrator."""
    ml_dir = Path(__file__).resolve().parent.parent.parent / 'ml'
    ml_dir_str = str(ml_dir)
    if ml_dir_str not in sys.path:
        sys.path.insert(0, ml_dir_str)


def get_career_orchestrator():
    """Get or create the singleton CareerOrchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _ensure_ml_path()
        from src.career.career_orchestrator import CareerOrchestrator
        _orchestrator = CareerOrchestrator()
    return _orchestrator


class CareerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'career'

    def ready(self):
        _ensure_ml_path()
