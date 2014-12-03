# coding:utf-8
from functools import wraps

from celery.execute import send_task
from celeryconfig import all_files


def pub(reciev=None):
    def _my_decorator(process):
        def _decorator(item, *args, **kwargs):
            result = process(item, *args, **kwargs)
            try:
                next_task = all_files[all_files.index(process.__module__) + 1]
                q = next_task.split('.')[1]
                if reciev:
                    q = reciev
                send_task(next_task, [result, ], queue=q)
            except Exception:
                pass
            return result
        return wraps(process)(_decorator)
    return _my_decorator
