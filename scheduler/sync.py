#!/usr/bin/env python
# coding:utf-8
import redis
from torndb import Connection

from models import Domain, Flow, Rule
import settings

rd = redis.Redis(settings.REDIS_HOST, settings.REDIS_PORT)
db = Connection('127.0.0.1', 'spider', user='spider', password='huangwei')

domains = db.query("select * from domain")

for d in domains:
    domain = Domain(rd, d["domain"])
    domain.update(d)
    if "scheduled" not in domain:
        domain["scheduled"] = 0

    rule_datas = db.query("select * from rule where domain = %s", d["domain"])
    for rule_data in rule_datas:
        rule = Rule(rd, d["domain"])
        rule.update(rule_data)

    flows = db.query("select * from flow where domain = %s", d["domain"])
    for f in flows:
        flow = Flow(rd, f["flow"])
        flow.update(f)
        if "scheduled" not in flow:
            flow["scheduled"] = 0
