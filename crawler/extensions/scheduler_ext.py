# coding:utf-8
from scrapy import signals
from scrapy.exceptions import DontCloseSpider


class SchedulerExtension(object):
    def __init__(self, settings):
        self.settings = settings

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings

        ext = cls(settings)
        crawler.signals.connect(ext.spider_idle, signal=signals.spider_idle)

        return ext

    def spider_idle(self, spider):
        if spider.name == "main":
            raise DontCloseSpider
