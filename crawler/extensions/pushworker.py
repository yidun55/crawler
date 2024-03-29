# coding:utf-8
import os
import sys
import time
import json

import redis
import pymongo
import pyreBloom
from scrapy import signals

base = os.path.realpath(os.path.join(os.path.dirname(__file__), 'processing'))
sys.path.append(base)
from processing.process import emit


class PushWorkerExtension(object):
    """发送车源信息到数据处理队列，同时存入mongodb"""
    def __init__(self, settings):
        self.settings = settings
        host = settings.get("REDIS_HOST")
        port = settings.get("REDIS_PORT")
        db = settings.get("LOG_REDIS_DB")
        self.rd = redis.Redis(host, port, db)
        self.urls_seen = pyreBloom.pyreBloom("bloomfilter", 100000000, 0.001,
                                             host=host, port=port)

        mongo_server = settings.get("MONGO_SERVER")
        mongo_port = settings.get("MONGO_PORT")
        mongo_db = settings.get("MONGO_DB")
        conn = pymongo.Connection(host=mongo_server, port=mongo_port)
        self.db = conn[mongo_db]

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        ext = cls(settings)
        crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)

        return ext

    def item_scraped(self, item, spider):
        data = dict(item)
        for x in item:
            if x.startswith("_"):
                del data[x]

        ldata = {
            "url": item["url"], "domain": item["domain"],
            "flow": ""
        }
        self.rd.zadd("log:scraped", json.dumps(ldata), time.time())

        self.db.car_info.update({'url': data['url']}, data, upsert=True)
        self.urls_seen.add(data['url'])
        emit(data)
        spider.log("Available Item send to worker, %s" % str(item))
