# coding: utf-8
import re
from hashlib import md5
from collections import defaultdict

import redis
from scrapy.conf import settings
from scrapy.http import Request
from scrapy.contrib.spiders import CrawlSpider
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from crawler.items import CrawlerItem
from crawler.spiders import further_request
from crawler.lib.models import Domain, Flow, Rule
from crawler.lib.selector import JsonPathSelector


class SuperSpider(CrawlSpider):
    name = "main"

    def __init__(self, *a, **kw):
        super(SuperSpider, self).__init__(*a, **kw)

        self.rd = redis.Redis(settings.get("REDIS_HOST"), settings.get("REDIS_PORT"),
                              db=settings.get("MAIN_REDIS_DB"))

        domain = settings.get("DOMAIN")
        self.domain = Domain(self.rd, domain)
        self.rule = Rule(self.rd, domain)
        settings.overrides['DOWNLOAD_DELAY'] = float(self.domain["download_delay"])
        settings.overrides['CONCURRENT_REQUESTS'] = int(self.domain["concurrent_requests"])

    def _get_realurl(self, response, url):
        if url.startswith("http://"):
            u = url
        else:
            u = urljoin_rfc(get_base_url(response), url)

        return u

    def parse(self, response):
        flow = Flow(self.rd, response.meta["flow"])

        page_no, = response.xpath(flow['pageno_xpath']).re(flow['pageno_regex'])
        if int(page_no) != int(flow["page_limit"]):
            next_pages = response.xpath(flow['list_page_xpath']).re(flow['list_page_regex'])
            for u in next_pages:
                yield Request(url=self._get_realurl(response, u),
                              meta=response.meta, callback=self.parse)

        detail_pages = response.xpath(flow['detail_page_xpath']).re(flow['detail_page_regex'])
        for u in detail_pages:
            yield Request(url=self._get_realurl(response, u),
                          meta=response.meta, callback=self.parse_item)

    def _load_raw(self, rule, response, jps, sep=''):
        raw = ""
        if rule:
            p_type, rule_case = rule.split("##")
            if p_type == 'xpath':
                xpath, regex = rule_case.split("#")
                rs = response.xpath(xpath).re(regex)
            elif p_type == 'jpath':
                rs = jps.jpath(rule_case)
            elif p_type == 'value':
                rs = [rule_case]
            elif p_type == 'regex':
                rs = re.findall(rule_case, response.body)

            raw = sep.join(s.strip() for s in rs)

        return raw

    def parse_item(self, response):
        jps = JsonPathSelector(response)

        item = CrawlerItem()
        item["url"] = response.url
        item["id"] = md5(response.url).hexdigest()
        item["domain"] = self.domain.name
        item["site"] = self.domain["domain_name"]
        item["flow"] = response.meta["flow"]
        item["version"] = "1.6"

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
                item[key] = self._load_raw(rule, response, jps, sep=sep)

        seq = 1
        max_seq = len(frs) + 1
        if frs:
            for fr, cates in frs.items():
                fr_func = further_request.__getattribute__(fr)
                frequest = fr_func(response)
                if frequest:
                    frequest.meta["fr"] = cates
                    frequest.meta["url"] = response.url
                    frequest.meta["id"] = item["id"]
                    frequest.meta["max_seq"] = max_seq
                    frequest.meta["seq"] = seq
                    frequest.callback = self.further_parse

                    yield frequest
                    seq += 1

        if seq == 1:
            seq = 0
        item["_max_seq"] = max_seq
        item["_seq"] = seq

        yield item

    def further_parse(self, response):
        jps = JsonPathSelector(response)

        item = CrawlerItem()
        cates = response.meta["fr"]
        for key, rule in cates.items():
            item[key] = self._load_raw(rule, response, jps)

        item["url"] = response.meta["url"]
        item["id"] = response.meta["id"]
        item["_max_seq"] = response.meta["max_seq"]
        item["_seq"] = response.meta["seq"]

        return item
