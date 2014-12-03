# coding:utf-8
from celery.task import task

from process import pub


@pub
@task
def process(item):
    return item * 2
