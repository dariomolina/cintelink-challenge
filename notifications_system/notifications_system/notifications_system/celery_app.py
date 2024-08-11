from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notifications_system.settings.local')

app = Celery(
    main='notifications_system',
    broker=settings.REDIS_LOCATION,
    result_backend=settings.REDIS_LOCATION,
)
app.conf.update(
    enable_utc=False,
    broker_connection_retry_on_startup=True
)
app.config_from_object(settings, namespace='CELERY')
app.autodiscover_tasks()


# app.conf.beat_schedule = {
#     'fetch-every-10-seconds': {
#         'task': 'ticker.tasks.fetch_and_set_buenbit_data',
#         'schedule': 10.0,  # Every 10 seconds
#     },
# }
