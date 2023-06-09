from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .search import search_in_google_map
from .models import Condition
import random
import datetime


@shared_task
def run_search(condition_id):
    # condition = Condition.objects.get(id = condition_id)
    condition = Condition.objects.all()
    for condition in condition:
        now = datetime.datetime.now().time()
        if condition.scheduled_start_time <= now <= condition.scheduled_end_time:
            # latitude = condition.latitude
            # longitude = condition.longitude
            # key_words = condition.key_words
            search_in_google_map(condition, condition.latitude,
                                 condition.longitude, condition.key_words)
    return "Search tasks completed"
