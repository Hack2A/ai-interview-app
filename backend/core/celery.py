"""Celery application configuration for Beaver AI."""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('beaver_ai')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Queue routing
app.conf.task_routes = {
    'whatsapp.tasks.process_whatsapp_message': {'queue': 'whatsapp'},
    'whatsapp.tasks.send_interview_reminders':  {'queue': 'default'},
}

app.conf.task_default_priority = 5
app.conf.task_acks_late = True  # re-queue on worker crash

# Beat schedule for reminders
app.conf.beat_schedule = {
    'send-interview-reminders': {
        'task': 'whatsapp.tasks.send_interview_reminders',
        'schedule': 300.0,  # every 5 minutes
    },
}
