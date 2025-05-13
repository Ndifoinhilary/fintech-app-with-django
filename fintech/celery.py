import os

from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fintech.settings.local')

app = Celery('Fintech Bank')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)



@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')