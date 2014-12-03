# coding:utf-8
from hashlib import md5

import redis
import pyreBloom
from scrapy.dupefilter import BaseDupeFilter
from scrapy import log


class RFPDupeFilter(BaseDupeFilter):
    """Request Fingerprint duplicates filter"""

    def __init__(self, settings):
        host = settings.get("REDIS_HOST")
        port = settings.get("REDIS_PORT")
        sdb = settings.get("SLICE_REDIS_DB")
        self.srd = redis.Redis(host, port, sdb)
        self.logdupes = True

        self.urls_seen = pyreBloom.pyreBloom("bloomfilter", 100000000, 0.001,
                                             host=host, port=port)

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)

    def request_seen(self, request):
        if request.url in self.urls_seen:
            return True

    def log(self, request, spider):
        # remove slice item in redis slice db, because it no longer to use
        car_id = md5(request.url).hexdigest()
        self.srd.delete(car_id)

        if self.logdupes:
            fmt = "Filtered duplicate request: %(request)s - no more duplicates will be shown (see DUPEFILTER_CLASS)"
            log.msg(format=fmt, request=request, level=log.DEBUG, spider=spider)
            self.logdupes = False
