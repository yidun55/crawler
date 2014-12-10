# coding:utf-8
import os


BROKER_URL = 'amqp://guest:guest@localhost:5672//'

tasks_loc = "tasks"
tasks_loc = os.path.realpath(os.path.join(os.path.dirname(__file__), "tasks"))
all_files = [f for f in os.listdir(tasks_loc)
             if f.endswith(".py") and f != '__init__.py']

CELERY_IMPORTS = ["tasks.{}".format(f[:-3]) for f in all_files]
CELERY_ACCEPT_CONTENT = ['json', ]
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_DEFAULT_EXCHANGE = 'car'
CELERY_DEFAULT_EXCHANGE_TYPE = 'topic'
#CELERY_DEFAULT_QUEUE = 'a'
#CELERY_DEFAULT_ROUTING_KEY = 'tasks.a.#'

CELERY_QUEUES = {
    f[:-3]: {'routing_key': 'tasks.{}.#'.format(f[:-3])}
    for f in all_files
}

CELERY_ROUTES = {
    f[:-3]: {
        'queue': f[:-3],
        'routing_key': 'tasks.{}.#'.format(f[:-3])
    }
    for f in all_files
}
