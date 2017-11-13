#! python3
# -*- coding: utf-8 -*-
from celery import Celery
from kombu import Exchange, Queue
from celery import platforms


platforms.C_FORCE_ROOT = True
tasks = ['tasks.generate_time', 'tasks.generate_json_url', 'tasks.crawl_json_url']
app = Celery('qq_task', include=tasks, broker='redis://127.0.0.1:6379/2', backend='redis://127.0.0.1:6379/3')
app.conf.update(
    CELERY_TIMEZONE='Asia/Shanghai',
    CELERY_ENABLE_UTC=True,
    CELERY_ACCEPT_CONTENT=['json'],
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json',
    CELERY_QUEUES=(
       Queue('page_one_queue', exchange=Exchange('page_one', type='direct'), routing_key='for_page_one'),
   )
)
