# coding:utf-8
from importlib import import_module

from celeryconfig import CELERY_IMPORTS


def emit(item):
    modules = [import_module(m) for m in CELERY_IMPORTS]
    m = modules[0]
    st = m.process.subtask((item, ), queue=m.__name__.split('.')[1])
    for m in modules[1:]:
        st |= m.process.subtask(queue=m.__name__.split('.')[1])

    return st()
