#coding: utf-8
from hashlib import md5
from collections import defaultdict

import redis
from scrapy import log
from scrapy.conf import settings
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.spiders import CrawlSpider
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from crawler.items import CrawlerItem
from crawler.spiders import further_request
from crawler.lib.models import Domain, Flow, Rule
from crawler.lib.selector import JsonPathSelector

class SuperSpider(CrawlSpider):
    name = "test"

    def __init__(self, *a, **kw):
        super(SuperSpider, self).__init__(*a, **kw)
        self.rd = redis.Redis(settings.get("REDIS_HOST"), settings.get("REDIS_PORT"),
                              db=settings.get("MAIN_REDIS_DB"))
        
        domain = settings.get("DOMAIN")
        self.domain = Domain(self.rd, domain)
        self.rule = Rule(self.rd, domain)
        settings.overrides['SCHEDULER'] = "scrapy.core.scheduler.Scheduler"
        settings.overrides['DOWNLOAD_DELAY'] = float(self.domain["download_delay"])
        settings.overrides['CONCURRENT_REQUESTS'] = int(self.domain["concurrent_requests"])
        
    def start_requests(self):
        start_urls = settings.getlist("URL")
        for url in start_urls:
            request = Request(url=url, callback=self.parse_item, dont_filter=True)
            request.meta["flow"] = "test"
            yield request

    def _load_raw(self, rule, hxs, jps, sep=''):
        raw = ""
        if rule:
            p_type, rule_case = rule.split("##")
            if p_type == 'xpath':
                xpath, regex = rule_case.split("#")
                rs = hxs.select(xpath).re(regex)
            elif p_type == 'jpath':
                rs = jps.jpath(rule_case)
                
            raw = sep.join(s.strip() for s in rs)

        return raw

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)
        jps = JsonPathSelector(response)

        item = CrawlerItem()
        item["url"] = response.url
        item["id"] = md5(response.url).hexdigest()

        frs = defaultdict(dict)
        for key, rule in self.rule.items():
            try:
                rule = rule.decode("utf-8")
            except:
                pass
                
            if key == "domain":
                item[key] = rule
                continue

            sep = ""
            if key == "car_images":
                sep = "###"
            if rule.startswith("fr"):
                _, func, frule = rule.split("###")
                frs[func][key] = frule
            else:
                item[key] = self._load_raw(rule, hxs, jps, sep=sep)

        seq = 1
        max_seq = len(frs) + 1
        if frs:
            for fr, cates in frs.items():
                fr_func = further_request.__getattribute__(fr)
                frequest = fr_func(response)
                frequest.meta["fr"] = cates
                frequest.meta["url"] = response.url
                frequest.meta["id"] = item["id"]
                frequest.meta["max_seq"] = max_seq
                frequest.meta["seq"] = seq
                frequest.callback = self.further_parse
                
                yield frequest
                seq += 1

        if seq == 1: seq = 0
        item["_max_seq"] = max_seq
        item["_seq"] = seq
        
        yield item

    def further_parse(self, response):
        hxs = HtmlXPathSelector(response)
        jps = JsonPathSelector(response)
        
        item = CrawlerItem()
        cates = response.meta["fr"]
        for key, rule in cates.items():
            item[key] = self._load_raw(rule, hxs, jps)

        item["url"] = response.meta["url"]
        item["id"] = response.meta["id"]
        item["_max_seq"] = response.meta["max_seq"]
        item["_seq"] = response.meta["seq"]

        return item
