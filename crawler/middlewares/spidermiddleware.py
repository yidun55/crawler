#coding:utf-8
import time
import json

import redis
from scrapy.http import Request

from crawler.items import CrawlerItem


class FlowMiddleware(object):
    def process_spider_output(self, response, result, spider):
        flowid = response.request.meta['flow']
        for req in result:
            if isinstance(req, Request):
                req.meta['flow'] = flowid
            yield req


class SpiderMiddleware(object):
    def __init__(self, settings):
        host = settings.get("REDIS_HOST")
        port = settings.get("REDIS_PORT")
        db = settings.get("LOG_REDIS_DB")
        self.rd = redis.Redis(host, port, db)
        self.settings = settings

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings)

    def process_spider_input(self, response, spider):
        data = {
            "url": response.url, "domain": self.settings.get("DOMAIN"),
            "flow": response.meta["flow"]
        }
        self.rd.zadd("log:spider:in", json.dumps(data), time.time())

    def process_spider_output(self, response, result, spider):
        for rs in result:
            if isinstance(rs, CrawlerItem):
                data = {
                    "url": response.url, "domain": self.settings.get("DOMAIN"),
                    "flow": response.meta["flow"]
                }
                self.rd.zadd("log:spider:out", json.dumps(data), time.time())
            yield rs

    def process_spider_exception(self, response, exception, spider):
        data = {
            "url": response.url, "domain": self.settings.get("DOMAIN"),
            "flow": response.meta["flow"]
        }
        self.rd.zadd("log:spider:error", json.dumps(data), time.time())
