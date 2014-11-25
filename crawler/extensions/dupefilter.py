import os
from hashlib import md5

import redis
from scrapy.dupefilter import BaseDupeFilter
from scrapy.utils.request import request_fingerprint
from scrapy.utils.job import job_dir
from scrapy import log

class RFPDupeFilter(BaseDupeFilter):
    """Request Fingerprint duplicates filter"""

    def __init__(self, settings):
        host = settings.get("REDIS_HOST")
        port = settings.get("REDIS_PORT")
        db = settings.get("FP_REDIS_DB")
        sdb = settings.get("SLICE_REDIS_DB")
        self.rd = redis.Redis(host, port, db)
        self.srd = redis.Redis(host, port, sdb)
        self.logdupes = True

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)

    def request_seen(self, request):
        m = md5(request.url).hexdigest()
        if self.rd.exists(m):
            return True

    def log(self, request, spider):
        # remove slice item in redis slice db, because it no longer to use
        car_id = md5(request.url).hexdigest()
        self.srd.delete(car_id)
        
        if self.logdupes:
            fmt = "Filtered duplicate request: %(request)s - no more duplicates will be shown (see DUPEFILTER_CLASS)"
            log.msg(format=fmt, request=request, level=log.DEBUG, spider=spider)
            self.logdupes = False