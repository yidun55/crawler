# coding: utf-8
import time

import redis

import logger
from models import Flow, Domain
from config import settings


class FlowAggr:
    def __init__(self, domain, prio):
        self.rd = redis.Redis(host=settings.REDIS_HOST,
                              port=settings.REDIS_PORT)
        self.domain = domain
        self.prio = prio
        self.logger = logger.getLogger("FA#%s-%s" % (self.domain.name, self.prio))

    def get_flows(self, **condition):
        """all flows under this domain
        """
        flows = Flow.filter(self.rd, domain=self.domain.name,
                            priority=self.prio, **condition)
        return flows

    def flow_exist(self, flowid):
        flow = Flow(self.rd, flowid)
        return flow['domain'] == self.domain.name and flow['priority'] == str(self.prio)

    def del_all_flows(self):
        'remove all flows in the flow aggregator'
        for flow in self.get_flows():
            flow.reset()

    def num_urls(self):
        '''total number of urls in the flow aggr'''
        return sum(flow.q_len() for flow in self.get_flows())

    def get_total_weights(self, flows=None):
        '''total weights of all flows'''
        if flows is None:
            flows = self.get_flows()
        return sum(int(flow['weight']) for flow in flows)

    def get_total_scheduled(self, flows=None):
        '''total scheduled urls during current cycle'''
        if not flows:
            flows = self.get_flows()
        return sum(int(flow['scheduled']) for flow in flows)

    def reset_schedule_cycle(self):
        '''
        This is introduced as a session delimiter, since we want to spread
        dequeue operation among multiple, consecutive schedule intervals. For
        example, each scheduling interval is 10 seconds, during which we
        may not have enough capacity to give each flow a fair share of URLs to
        download. But if we spread a scheduling cycle of 1 hour into multiple
        scheduling interval, we may be able to give each flow its fair share.
        '''
        for flow in self.get_flows():
            flow['scheduled'] = 0

    def deque(self, num):
        '''
        Dequeue num objects from the aggregate. "num" is number of urls
        that need to be dequed during this interval, for this flow aggr.

        Return a list of objects dequeud.
        '''
        # first calculate for each flow how many urls needs to be scheduled
        # during current interval, filter out non-positive ones.
        # next calculate how many urls available for each flow that can be
        # scheduled. Loop until either there is no available urls
        # to schedule or the total number is reached.
        n = num
        flows = [f for f in self.get_flows() if f.q_len() > 0 and f['enabled'] == '1']
        init_sched = prev_sched = self.get_total_scheduled(flows)
        while n>0 and flows:
            total_weights = self.get_total_weights(flows)
            for f in flows:
                num_sched = int(f['weight']) * (n+prev_sched) / total_weights
                actual = num_sched - int(f['scheduled'])
                if actual > n:
                    actual = n
                if actual == 0:
                    actual = 1
#                self.logger.debug("@%d--%s: %d/%s" \
#                                  % (f.name, f['scheduled'], num_sched, actual))
                if actual > 0:
                    for url in f.q_mpop(actual):
                        n -= 1
                        f.incr('scheduled')
                        yield url

            flows = [f for f in flows if f.q_len()>0]
            prev_sched = self.get_total_scheduled(flows)
#        self.logger.debug("requesting=%d, previously sched=%d, dequeued=%d", num, init_sched, num-n)


class PrioQueue:
    '''
    Abstraction of the priority queue for a domain. This is basically a container
    of all flow aggreagators.
    '''
    def __init__(self, domain):
        self.rd = redis.Redis(host=settings.REDIS_HOST,
                              port=settings.REDIS_PORT)
        self.domain = domain
        self.flowaggrs = {}
        self.prios = self.get_prios()
        for prio in self.prios:
            self.flowaggrs[prio] = FlowAggr(domain, prio)
        self.logger = logger.getLogger("PQ#%s" % (self.domain.name))

    def get_prios(self):
        '''
        Get all priorities for a given domain.
        '''
        sf = Flow.filter(self.rd, domain=self.domain.name)
        return sorted(set(s['priority'] for s in sf))

    def pq_len(self, prio):
        '''return the length of the queue corresponding to a priority.
        '''
        if prio in self.flowaggrs:
            return self.flowaggrs[prio].num_urls()
        else:
            return 0

    def flow_exist(self, flowid):
        '''does the flow exist in the priority queue?'''
        for prio in self.flowaggrs:
            if self.flowaggrs[prio].flow_exist(flowid):
                return True
        return False

    def reset_schedule_cycle(self):
        for prio in self.prios:
            self.flowaggrs[prio].reset_schedule_cycle()

    def deque(self, num):
        '''
        Deque num urls. "num" is the number of urls that need to be dequeued
        during this interval.
        '''
        # Starts from highest priority to the lowest.
        n = num
        scheduled = 0
        for prio in self.flowaggrs:
            fa = self.flowaggrs[prio]
            for url in fa.deque(n):
                scheduled += 1
                yield url
            n = num - scheduled
            if n <= 0:
                break
#        self.logger.info("total %d urls scheduled", scheduled)


class DomainController:
    '''
    a wrapper of request queue.
    '''
    def __init__(self, domain):
        self.rd = redis.Redis(host=settings.REDIS_HOST,
                              port=settings.REDIS_PORT)
        self.domain = domain
        self.logger = logger.getLogger("#%s" % (self.domain.name))

    def num_urls_to_schedule_interval(self, interval):
        max_urls = int(self.domain.get('maxurls', settings.MAX_URLS_PER_INTERVAL))

        urls_intvl = (interval+1) * max_urls - int(self.domain['scheduled'])
        outstanding = self.domain.q_len()

        if outstanding == 0:
            n = min(2*max_urls, urls_intvl)
        elif outstanding < max_urls:
            n = min(max_urls, urls_intvl)
        else:
            # why feed more, if the previous feed has not been consumed
            n = 0
        return n

    def reset_schedule_cycle(self):
        self.domain['scheduled'] = 0

    def reset(self):
        self.domain.reset()


class Schd:
    def __init__(self):
        self.rd = redis.Redis(host=settings.REDIS_HOST,
                              port=settings.REDIS_PORT)
        self.schedule_interval = settings.SCHEDULE_INTERVAL
        self.intervals_per_cycle = settings.INTERVALS_PER_CYCLE
        self.mon = None
        self.logger = logger.getLogger("Scheduler")

    def set_monitor(self, mon):
        self.mon = mon

    def get_domains(self):
        """return the all domains as a generator, from start to finish, inclusive.
        """
        return Domain.filter(self.rd)

    def run_interval(self, interval_offset):
        """
        During each scheduling interval, scheduler will do the following:
        1. Find all domains that needs to schedule.
        2. For each domains, calculate the total number of URLs that can be
           allowed during this cycle.
        3. Request URLs from each priority queue, highest priority first,
           starting with the number calaculated in step #2.
           the remaining number from the 2nd highest priority queue, etc.
        4. For each priority queue, request from each of the containing
           flow URLs using weighted round robin policy.
        5. Put all scheduled URLs into each domain's 'request queue'.

        @param interval_offset: indicate the offset within a scheduling cycle.
        We want to have these cycle/interval tiers to achieve two purposes:
           * to have urls scheduled quickly, therefore shorter intervals
           * to have accurate calculation of URL numbers per flow therefore needs
             longer intervals to have big enough number to get meaningful results.
        """
        self.logger.info("Interval cycle: <%d>.", interval_offset)
        for domain in self.get_domains():
            spd_ctrl = DomainController(domain)
            pq = PrioQueue(domain)
            if interval_offset == 0:
                spd_ctrl.reset_schedule_cycle()
                pq.reset_schedule_cycle()
            num_urls = spd_ctrl.num_urls_to_schedule_interval(interval_offset)

            anum = 0
            if num_urls > 0:
                for url_req in pq.deque(num_urls):
                    spd_ctrl.domain.q_push(url_req)
                    anum += 1

            self.logger.info("<%d>#%s, Require %d, Actual %d, Queue count %d" \
                             % (interval_offset, domain.name, num_urls, anum, domain.q_len()))

    def scheduler(self):
        """scheduler main loop"""
        interval = 0
        while True:
            if self.mon:
                self.mon.do_monitor_interval()
            self.run_interval(interval)
            interval += 1
            if interval == self.intervals_per_cycle:
                interval = 0
            time.sleep(self.schedule_interval)
