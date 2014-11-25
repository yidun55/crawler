#coding: utf-8
import time
import json
from hashlib import md5

from scrapy.exceptions import DropItem

import redis
from scrapy import log


class CrawlerPipeline(object):
    def __init__(self, settings):
        self.settings = settings
        host = settings.get("REDIS_HOST")
        port = settings.get("REDIS_PORT")
        db = settings.get("LOG_REDIS_DB")
        # Fingerprint DB
        fp_db = settings.get("FP_REDIS_DB")
        slice_db = settings.get("SLICE_REDIS_DB")
        self.log_rd = redis.Redis(host, port, db)
        self.fp_rd = redis.Redis(host, port, fp_db)
        self.slice_rd = redis.Redis(host, port, slice_db)

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)

    def process_item(self, item, spider):
        full_item = item.copy()
        if item["_seq"] > 0:
            self.slice_rd.sadd(item["id"], json.dumps(dict(item)))
            self.slice_rd.expire(item["id"], 3600)
            if self.slice_rd.scard(item["id"]) == item["_max_seq"]:
                for i in self.slice_rd.smembers(item["id"]):
                    full_item.update(json.loads(i))
                self.slice_rd.delete(item["id"])
            else:
                raise DropItem("Further slice item.")

        # create time/updated time
        full_item["created"] = int(time.time() * 1000)
        full_item["updated"] = full_item["created"]

        # save fingerprint to redis
        if spider.name == "main":
            m = md5(full_item["url"]).hexdigest()
            c = md5(json.dumps(dict(full_item))).hexdigest()
            self.fp_rd.set(m, c)
            self.fp_rd.expire(m, self.settings.get("FP_EXPIRE"))

        return full_item
