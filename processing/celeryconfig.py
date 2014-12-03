# coding:utf-8
import os


BROKER_URL = 'amqp://guest:guest@localhost:5672//'

tasks_loc = "tasks"
all_files = (f for f in os.listdir(tasks_loc)
             if f.endswith(".py") and f is not '__init__.py')
CELERY_IMPORTS = ["{}.{}".format(tasks_loc, f[:-3]) for f in all_files]
#CELERY_IMPORTS = ('tasks.a', 'tasks.b')
CELERY_ACCEPT_CONTENT = ['json', ]
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_DEFAULT_EXCHANGE = 'car'
CELERY_DEFAULT_EXCHANGE_TYPE = 'topic'
#CELERY_DEFAULT_QUEUE = 'a'
#CELERY_DEFAULT_ROUTING_KEY = 'tasks.a.#'


#CELERY_QUEUES = (
#    Queue('a', routing_key='tasks.a.#'),
#    Queue('b', routing_key='tasks.b.#'),
#)
CELERY_QUEUES = {
    f[:-3]: {'routing_key': '{}.{}.#'.format(tasks_loc, f[:-3])}
    for f in all_files
}
#CELERY_ROUTES = {
#    'a': {
#        'queue': 'a',
#        'routing_key': 'tasks.a.#',
#    },
#    'b': {
#        'queue': 'b',
#        'routing_key': 'tasks.b.#',
#    },
#}

CELERY_ROUTES = {
    f[:-3]: {
        'queue': f[:-3],
        'routing_key': '{}.{}.#'.format(tasks_loc, f[:-3])
    }
    for f in all_files
}
