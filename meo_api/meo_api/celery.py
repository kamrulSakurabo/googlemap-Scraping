from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meo_api.settings')

app = Celery('meo_api')

# This reads, e.g., CELERY_BROKER_URL from your Django settings:
app.config_from_object('django.conf:settings', namespace='CELERY')

# This will make Celery discover tasks from all registered Django apps:
app.autodiscover_tasks()

# define the periodic task (schedule)
app.conf.beat_schedule = {
    'run_search_everyday': {
        'task': 'api.tasks.run_search',
        'schedule': crontab(hour=7, minute=30),
    }
}

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

