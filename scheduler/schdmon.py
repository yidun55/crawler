#coding: utf-8
import time
import json

import redis
from scrapy.http import Request
from scrapy.utils.reqser import request_to_dict, request_from_dict

import logger
from config import settings
from models import Flow

class SchdMon:
    def __init__(self):
        self.logger = logger.getLogger("*Monitor*")

        self.rd = redis.Redis(host=settings.REDIS_HOST,
                              port=settings.REDIS_PORT)

        # initial state and values
        for flow in self.get_all_flows():
            if not 'scheduled' in flow:
                flow['scheduled'] = 0
            flow['state'] = 'stopped'
            flow['last_scheduled'] = flow['scheduled']
            flow['noact'] = 0
        
    def get_all_flows(self):
        '''get all flow ids'''
        return Flow.filter(self.rd)
    
    def check_to_resch(self, flow, start, end):
        """check a stopped flow to see if we need to reschedule it. 
        start and end are the last run's start and finish time.
        """
        resch_period = int(flow.get("interval", 0))
        if time.time()-start > resch_period:
            if not 'seeds' in flow:
                self.logger.info("flow %s: seed url not found", flow.name)
            for url in flow['seeds']:
                req = Request(url)
                req.meta['flow'] = flow.name
                data = json.dumps(request_to_dict(req))
                flow.q_push(data)

            flow['state'] = 'ready'
            self.logger.info("flow %s: seed inserted, ready-to-go", flow.name)

    def generate_run_rec(self, flow, start_time, stop_time):
        """create a history record."""
        key = "run-rec:%s:flow:%s" % (flow['parent'], flow.name)
        settings.RD.rpush(key, "%d:%d" % (int(start_time), int(stop_time)))

    def do_monitor_interval(self):
        """Iterate through all flows and for each flow do the following:
          * initially last_scheduled is set to scheduled and run-state is set to 'stopped'
          * compare the last_scheduled with scheduled. 
              ** If same and the run-state is 'running', increase noact counter.
              ** If not the same, set last_scheduled to scheduled. If the state is 
                 'stopped' and scheduled is not 0, change the state to 'running' 
                 and update start_time of the run. If the state is 'running', reset
                 'noact' counter.
          * if noact reached a threshold, declare the state to be 'stopped' and
            create a history record for the past run. Then examine the configuration
            of the flow and decide if we should schedule the next run. If we should,
            enque the seed url into the flow queue.
        """
        for flow in self.get_all_flows():
            if flow['enabled'] != '1':
                continue
            if not 'last_scheduled' in flow:  # newly added flow during runtime
                flow['state'] = "stopped"
                flow['last_scheduled'] = 0
                flow['scheduled'] = 0
                flow['noact'] = 0

            sched = int(flow['scheduled'])
            last_sched = int(flow['last_scheduled'])
            state = flow.get('state')
            start_time = int(float(flow.get('start_time', 0)))
            stop_time = int(float(flow.get('stop_time', 0)))
            if state == "running":
                if sched == last_sched and flow.q_len()==0:
                    noact = flow.incr('noact')
                    self.logger.info("$%s: no-act=%s", flow.name, noact)
                    if int(noact) >= 10 and int(flow['interval']):
                        stop_time = int(time.time())
                        flow['state'] = "stopped"
                        flow['stop_time'] = stop_time
                        flow['noact'] = 0
                        # create a history record
                        #self.generate_run_rec(flow, start_time, stop_time)
                        self.logger.info("$%s: stopped", flow.name)
                elif sched != last_sched:
                    flow['last_scheduled'] = sched
                    flow['noact'] = 0
            # stopped or ready
            else:
                if state == "stopped" and flow.q_len()==0:
                    self.check_to_resch(flow, start_time, stop_time)
                if last_sched != sched:
                    if sched == 0: # sched reset at new cycle
                        flow['last_scheduled'] = sched
                    else:
                        flow['state'] = 'running'
                        flow['start_time'] = int(time.time())
                        flow['last_scheduled'] = sched
                        flow['noact'] = 0
                        self.logger.info("$%s: started", flow.name)
                        
