import sys
from pathlib import Path
from django.apps import AppConfig

# Global orchestrator instance for REST views (lazy-loaded singleton)
_orchestrator = None


def _ensure_ml_path():
    """Add the ml/ directory to sys.path so we can import orchestrator."""
    ml_dir = Path(__file__).resolve().parent.parent.parent / 'ml'
    ml_dir_str = str(ml_dir)
    if ml_dir_str not in sys.path:
        sys.path.insert(0, ml_dir_str)


def get_orchestrator():
    """Get or create the singleton BeaverAI orchestrator for REST views.

    NOTE: The WebSocket consumer creates its OWN per-connection instance
    via _create_orchestrator() in consumers.py. This singleton is only
    for REST API endpoints (views.py).
    """
    global _orchestrator
    if _orchestrator is None:
        _ensure_ml_path()
        from orchestrator import BeaverAIOrchestrator
        _orchestrator = BeaverAIOrchestrator(lazy_load=True)
    return _orchestrator


class InterviewConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'interview'

    def ready(self):
        _ensure_ml_path()
