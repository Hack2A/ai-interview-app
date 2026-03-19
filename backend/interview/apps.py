import sys
from pathlib import Path
from django.apps import AppConfig

# Global orchestrator instance (lazy-loaded)
_orchestrator = None


def get_orchestrator():
    """Get or create the singleton BeaverAI orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        from orchestrator import BeaverAIOrchestrator
        _orchestrator = BeaverAIOrchestrator(lazy_load=True)
    return _orchestrator


class InterviewConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'interview'

    def ready(self):
        # Add the ml/ directory to sys.path so we can import orchestrator
        ml_dir = Path(__file__).resolve().parent.parent.parent / 'ml'
        ml_dir_str = str(ml_dir)
        if ml_dir_str not in sys.path:
            sys.path.insert(0, ml_dir_str)
