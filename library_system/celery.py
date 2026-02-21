import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')

app = Celery('library_system')

# Load config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'send-daily-admin-report': {
        'task': 'api.tasks.send_daily_admin_report',
        'schedule': crontab(hour=9, minute=0),  # Every day at 9:00 AM
    },
    'send-weekly-admin-report': {
        'task': 'api.tasks.send_weekly_admin_report',
        'schedule': crontab(day_of_week=1, hour=9, minute=0),  # Every Monday at 9:00 AM
    },
}

app.conf.timezone = 'Asia/Kolkata'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
