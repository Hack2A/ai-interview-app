from django.apps import AppConfig


class WhatsappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'whatsapp'
    verbose_name = 'WhatsApp Integration'

    def ready(self):
        # Ensures tasks are registered with Celery
        import whatsapp.tasks  # noqa: F401
