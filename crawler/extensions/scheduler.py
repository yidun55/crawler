import json

from scrapy.utils.reqser import request_to_dict, request_from_dict
from scrapy.utils.misc import load_object


class Scheduler(object):
    """Redis-based scheduler"""
    def __init__(self, dupefilter, domainclass=None,
                 flowclass=None, stats=None, settings=None):
        self.df = dupefilter
        self.domainclass = domainclass
        self.flowclass = flowclass
        self.stats = stats
        self.settings = settings

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        dupefilter_cls = load_object(settings['DUPEFILTER_CLASS'])
        dupefilter = dupefilter_cls.from_settings(settings)
        domainclass = load_object(settings['SCHEDULER_DOMAIN_CLASS'])
        flowclass = load_object(settings['SCHEDULER_FLOW_CLASS'])
        return cls(dupefilter, domainclass, flowclass, crawler.stats, settings)

    def has_pending_requests(self):
        return len(self) > 0

    def open(self, spider):
        self.spider = spider
        self.domainmodel = self.domainclass.from_settings(
            self.settings["DOMAIN"], self.settings)
        return self.df.open()

    def close(self, reason):
        return self.df.close(reason)

    def enqueue_request(self, request):
        if not request.dont_filter and self.df.request_seen(request):
            self.df.log(request, self.spider)
            return

        self.flowmodel = self.flowclass.from_settings(
            request.meta["flow"], self.settings)
        self._eqpush(request)
        self.stats.inc_value('scheduler/enqueued/redis', spider=self.spider)
        self.stats.inc_value('scheduler/enqueued', spider=self.spider)

    def next_request(self):
        request = self._dqpop()
        if request:
            self.stats.inc_value('scheduler/dequeued/redis', spider=self.spider)
            self.stats.inc_value('scheduler/dequeued', spider=self.spider)
        return request

    def __len__(self):
        return self.domainmodel.q_len()

    def _eqpush(self, request):
        req = json.dumps(request_to_dict(request, self.spider))
        self.flowmodel.q_push(req)

    def _dqpop(self):
        if self.domainmodel:
            d = self.domainmodel.q_pop()
            if d:
                return request_from_dict(json.loads(d), self.spider)
