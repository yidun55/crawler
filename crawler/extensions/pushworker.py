#coding:utf-8
import time
import json

import redis
import pymongo
from scrapy import signals

from crawler.lib.mq import MessageClient

class PushWorkerExtension(object):
    """发送车源信息到数据处理队列，同时存入mongodb"""
    def __init__(self, settings):
        self.settings = settings
        host = settings.get("REDIS_HOST")
        port = settings.get("REDIS_PORT")
        db = settings.get("LOG_REDIS_DB")
        self.rd = redis.Redis(host, port, db)
        self.mclient = MessageClient.from_settings(settings)

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

        self.mclient.send(data)
        ldata = {
            "url": item["url"], "domain": item["domain"],
            "flow": ""
        }
        self.rd.zadd("log:scraped", json.dumps(ldata), time.time())

        #self.db.car_info.save(data)
        spider.log("Available Item send to worker, %s" % str(item))
