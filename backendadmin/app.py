#!/usr/bin/env python
# coding: utf-8
"""backend webadmin
"""
import os
import time
import datetime
import logging
import json
from collections import defaultdict
from StringIO import StringIO

import xlwt
import redis
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.web import RequestHandler
from tornado.web import asynchronous
from tornado.options import define, options
from tornado.escape import json_encode, json_decode
from torndb import Connection

import settings
from models import Domain


class MyApplication(Application):
    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/schedule", ScheduleHandler),
            (r"/recently", RecentlyViewHandler),
            (r"/overview", OverViewHandler),
            (r"/domains", DomainsViewHandler),
            (r"/details", DomainDetailHandler),
        ]
        config = dict(
            template_path=os.path.join(os.path.dirname(__file__), settings.TEMPLATE_ROOT),
            static_path=os.path.join(os.path.dirname(__file__), settings.STATIC_ROOT),
            #xsrf_cookies=True,
            cookie_secret="__TODO:_E720135A1F2957AFD8EC0E7B51275EA7__",
            autoescape=None,
            debug=settings.DEBUG
        )
        Application.__init__(self, handlers, **config)

        self.rd_main = redis.Redis(settings.REDIS_HOST, settings.REDIS_PORT)
        self.db = Connection(
            host=settings.MYSQL_HOST, database=settings.MYSQL_DB,
            user=settings.MYSQL_USER, password=settings.MYSQL_PASS)


class BaseHandler(RequestHandler):
    @property
    def db(self):
        return self.application.db


class IndexHandler(BaseHandler):
    def get(self):
        self.redirect("/recently")


class ScheduleHandler(BaseHandler):
    def get(self):
        self.render('schedule.html', domains=Domain.filter(self.rd_main))


class RecentlyViewHandler(BaseHandler):
    def get(self):
        yestoday = datetime.datetime.today() - datetime.timedelta(days=1)
        before_yestday = datetime.datetime.today() - datetime.timedelta(days=2)

        rs = []
        for date in (yestoday, before_yestday):
            rs.append((get_data(self.db, date), get_count(self.db, date), date))

        self.render("last_view.html", datas=rs, cur_date=yestoday)


class OverViewHandler(BaseHandler):
    def get(self):
        today = datetime.datetime.today()
        default_start = (today - datetime.timedelta(days=20)).strftime("%Y-%m-%d")
        default_end = today.strftime("%Y-%m-%d")
        self.start = self.get_argument("start", default_start)
        self.end = self.get_argument("end", default_end)

        start_time = datetime.datetime.strptime(self.start, "%Y-%m-%d")
        end_time = datetime.datetime.strptime(self.end, "%Y-%m-%d")
        rs = []
        for date in date_xrange(start_time, end_time):
            rs.append((get_count(self.db, date), date))

        if self.get_argument("export", "null") == 'xls':
            self.export(rs)
        else:
            self.render("over_view.html", datas=rs, start_time=self.start, end_time=self.end)

    def export(self, datas):
        xls = xlwt.Workbook()
        sheet = xls.add_sheet(u"车源抓取情况")
        sheet.write(0, 0, u'日期')
        sheet.write(0, 1, u'网站数量')
        sheet.write(0, 2, u'历史车源总量')
        sheet.write(0, 3, u'在线车源总量')
        sheet.write(0, 4, u'新增抓取车源总量')
        sheet.write(0, 5, u'重复车源总量')
        sheet.write(0, 6, u'无效车源总量')
        sheet.write(0, 7, u'新增有效车源总量')

        line = 1
        for data in datas:
            date_str = data['date'].strftime('%Y-%m-%d')
            sheet.write(line, 0, date_str)
            sheet.write(line, 1, data['count']['domain_count'])
            sheet.write(line, 2, data['count']['old_total'])
            sheet.write(line, 3, data['count']['cur_total'])
            sheet.write(line, 4, data['count']['day_append'])
            sheet.write(line, 5, data['count']['day_duplicate'])
            sheet.write(line, 6, data['count']['day_overdue'])
            sheet.write(line, 7, data['count']['day_available'])
            line += 1

        f = StringIO()
        xls.save(f)

        self.set_header('Content-Type', 'application/vnd.ms-excel')
        self.set_header('Content-Disposition', u'attachment; filename=车源抓取情况%s~%s.xls' % (self.start, self.end))
        self.write(f.getvalue())


class DomainsViewHandler(BaseHandler):
    def get(self):
        yestoday = datetime.datetime.today() - datetime.timedelta(days=1)
        self.date = self.get_argument("date", yestoday.strftime("%Y-%m-%d"))
        date_time = datetime.datetime.strptime(self.date, "%Y-%m-%d")

        rs = get_data(self.db, date_time)

        if self.get_argument("export", "null") == 'xls':
            self.export(rs)
        else:
            self.render("domain_view.html", datas={"data": rs, "date": date_time})

    def post(self):
        domain = self.get_argument("domain")
        date = self.get_argument("date")
        content = self.get_argument("content")

        self.db.execute(
            "update statistics_processing set description = %s where domain = %s and date_str = %s",
            content, domain, date
        )

        self.write(content)

    def export(self, datas):
        xls = xlwt.Workbook()
        sheet = xls.add_sheet(u"网站分布情况")
        sheet.write(0, 0, 'NO.')
        sheet.write(0, 1, u'网站名称')
        sheet.write(0, 2, u'网站域名')
        sheet.write(0, 3, u'历史车源数量')
        sheet.write(0, 4, u'在线车源总量')
        sheet.write(0, 5, u'新增抓取车源总量')
        sheet.write(0, 6, u'重复车源总量')
        sheet.write(0, 7, u'无效车源总量')
        sheet.write(0, 8, u'新增有效车源总量')
        sheet.write(0, 9, u'状态')
        sheet.write(0, 10, u'备注异常')

        line = 1
        for data in datas['data']:
            sheet.write(line, 0, line)
            sheet.write(line, 1, data['domain_name'])
            sheet.write(line, 2, data['domain'])
            sheet.write(line, 3, data['old_total'])
            sheet.write(line, 4, data['cur_total'])
            sheet.write(line, 5, data['day_append'])
            sheet.write(line, 6, data['day_duplicate'])
            sheet.write(line, 7, data['day_overdue'])
            sheet.write(line, 8, data['day_available'])
            sheet.write(line, 9, data['status'])
            sheet.write(line, 10, '')
            line += 1

        f = StringIO()
        xls.save(f)
        self.set_header('Content-Type', 'application/vnd.ms-excel')
        self.set_header('Content-Disposition', u'attachment; filename=网站分布情况-%s.xls' % self.date)
        self.write(f.getvalue())


class DomainDetailHandler(BaseHandler):
    def get(self):
        today = datetime.datetime.today()
        default_start = (today - datetime.timedelta(days=20)).strftime("%Y-%m-%d")
        default_end = today.strftime("%Y-%m-%d")
        self.start = self.get_argument("start", default_start)
        self.end = self.get_argument("end", default_end)
        self.domain = self.get_argument("domain", "null")

        start_time = datetime.datetime.strptime(self.start, "%Y-%m-%d")
        end_time = datetime.datetime.strptime(self.end, "%Y-%m-%d")

        rs = []
        if self.domain != "null":
            for date in date_xrange(start_time, end_time):
                d = get_data(self.db, date, domain=self.domain)
                rs.append((d[0], date))

        if self.get_argument("export", 'null') == 'xls':
            self.export(rs)
        else:
            all_domains = self.db.query("select * from domain")
            all_domains.sort(key=lambda x: x["domain"])
            self.render("domain_detail.html", datas=rs, start_time=self.start,
                        end_time=self.end, cur_domain=self.domain, domains=all_domains)

    def export(self, datas):
        xls = xlwt.Workbook()
        sheet = xls.add_sheet(u"网站详情")
        sheet.write(0, 0, u'日期')
        sheet.write(0, 1, u'历史车源总量')
        sheet.write(0, 2, u'在线车源总量')
        sheet.write(0, 3, u'新增抓取车源总量')
        sheet.write(0, 4, u'重复车源总量')
        sheet.write(0, 5, u'无效车源总量')
        sheet.write(0, 6, u'新增有效车源总量')
        sheet.write(0, 7, u'备注异常')

        line = 1
        for data in datas:
            date_str = data['date'].strftime('%Y-%m-%d')
            sheet.write(line, 0, date_str)
            sheet.write(line, 1, data['count']['old_total'])
            sheet.write(line, 2, data['count']['cur_total'])
            sheet.write(line, 3, data['count']['day_append'])
            sheet.write(line, 4, data['count']['day_duplicate'])
            sheet.write(line, 5, data['count']['day_overdue'])
            sheet.write(line, 6, data['count']['day_available'])
            sheet.write(line, 7, data['count']['day_available'])
            line += 1

        f = StringIO()
        xls.save(f)
        self.set_header('Content-Type', 'application/vnd.ms-excel')
        self.set_header('Content-Disposition', u'attachment; filename=网站详情(%s).xls' % self.domain)
        self.write(f.getvalue())


def get_count(db, date):
    rs = {"domain_count": 31}
    date_str = date.strftime('%Y%m%d')
    sql = "select sum(old_total) as old_total, sum(cur_total) as cur_total from statistics_total where date_str = %s group by date_str"
    result = db.query(sql, date_str)
    if result:
        rs.update(result[0])
    else:
        rs.update({"old_total": 0, "cur_total": 0})

    sql = "select sum(scraped) as scraped from statistics_crawler where date_str = %s group by date_str"
    result = db.query(sql, date_str)
    if result:
        rs.update(result[0])
    else:
        rs.update({'scraped': 0})

    sql = "select sum(ignored) as total_ignore, sum(append) as append, sum(duplicated) as duplicated from statistics_processing where date_str = %s group by date_str"
    result = db.query(sql, date_str)
    if result:
        rs.update(result[0])
    else:
        rs.update({'total_ignore': 0, 'append': 0})

    return rs


def get_data(db, date, domain=None):
    totals = db.query("select * from statistics_total where date_str = %s", date.strftime('%Y%m%d'))
    totals = {t["domain"]: t for t in totals}

    sql = "select * from statistics_crawler where date_str = %s"
    if domain:
        sql += " and domain = '%s'" % domain
    datas = db.query(sql, date.strftime('%Y%m%d'))
    rs_datas = {data["domain"]: data for data in datas}

    sql = "select * from statistics_processing where date_str = %s"
    if domain:
        sql += " and domain = '%s'" % domain
    datas = db.query(sql, date.strftime('%Y%m%d'))
    rs_datas1 = {data["domain"]: data for data in datas}

    sql = "select * from statistics_total where date_str = %s"
    if domain:
        sql += " and domain = '%s'" % domain
    datas = db.query(sql, date.strftime('%Y%m%d'))
    rs_datas2 = {data["domain"]: data for data in datas}

    rs_row = rs_datas.copy()
    for x, y in rs_datas.items():
        y.update(rs_datas1.get(x, {}))
        y.update(rs_datas2.get(x, {}))
        rs_row[x] = y

    domains = db.query("select * from domain")
    result = []
    for domain in domains:
        rd = domain
        rd.update(totals.get(domain["domain"], {}))
        rd.update(rs_row.get(domain["domain"], {}))
        result.append(rd)

    result.sort(key=lambda x: x.get('cur_total', 0), reverse=True)
    return result


def date_xrange(start, end):
    curr = end
    while curr > start:
        curr -= datetime.timedelta(days=1)
        yield curr


if __name__ == '__main__':
    define("host", default=settings.DEFAULT_HOST, help="run on the given host")
    define("port", default=settings.DEFAULT_PORT, help="run on the given port", type=int)
    options.parse_command_line()

    http_server = HTTPServer(MyApplication())
    http_server.listen(port=options.port, address=options.host)

    IOLoop.instance().start()
