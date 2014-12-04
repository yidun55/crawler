# coding:utf-8
from celery.task import task


@task
def process(item):
    return item + 1
