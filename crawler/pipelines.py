# coding: utf-8
import json
import datetime

import redis
from scrapy.exceptions import DropItem


class CrawlerPipeline(object):
    def __init__(self, settings):
        self.settings = settings
        host = settings.get("REDIS_HOST")
        port = settings.get("REDIS_PORT")
        slice_db = settings.get("SLICE_REDIS_DB")
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
        full_item["created"] = datetime.datetime.now()
        full_item["updated"] = full_item["created"]

        return full_item
