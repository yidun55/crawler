# coding: utf-8
import time
import json

import redis
from scrapy.http import Response, HtmlResponse
from scrapy.exceptions import IgnoreRequest
from twisted.internet.error import TimeoutError


class DownloadMiddleware(object):
    """
    日志记录
    将每个请求与响应记录入redis
    """
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

    def process_request(self, request, spider):
        data = {
            "url": request.url, "domain": self.settings.get("DOMAIN"),
            "flow": request.meta["flow"]
        }
        if request.method == "POST":
            self.rd.zadd("log:httprequest:post", json.dumps(data), time.time())
        elif request.method == "GET":
            self.rd.zadd("log:httprequest:get", json.dumps(data), time.time())

    def process_response(self, request, response, spider):
        """将HTTP GET CODE在400到900之间的请求url写入废弃库，并抛弃这个请求"""
        # 记录日志以便统计
        data = {
            "url": request.url, "domain": self.settings.get("DOMAIN"),
            "flow": request.meta["flow"]
        }
        if response.status >= 400:
            #if response.status < 900:
            #    self.rd.zadd("url-trash", response.url, time.time())
            data["status"] = response.status
            self.rd.zadd("log:httpresponse:error", json.dumps(data), time.time())
            raise IgnoreRequest("Http code %s." % response.status)
        else:
            self.rd.zadd("log:httpresponse", json.dumps(data), time.time())
            return response

    def process_exception(self, request, exception, spider):
        """定义下载超时的HTTP CODE为900，然后转给process_response去处理"""
        data = {
            "url": request.url, "domain": self.settings.get("DOMAIN"),
            "flow": request.meta["flow"], "timestamp": time.time()
        }
        if isinstance(exception, TimeoutError):
            return Response(url=request.url, request=request, status=900)
        else:
            try:
                data["msg"] = exception.message
            except:
                data["msg"] = "unknow"
            self.rd.zadd("log:httperror:unknow", json.dumps(data), time.time())


class ResponseTransfer(object):
    """
    由于某些网站返回的Header没有指定content-type，所以scrapy默认的response为Response类型
    会导致htmlxpath选择器无法工作。
    这里将Response转换为HtmlResponse
    """
    def process_response(self, request, response, spider):
        if type(response) == Response:
            html_response = HtmlResponse(url=response.url, body=response.body, request=request)
            return html_response

        return response
