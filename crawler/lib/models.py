#coding: utf-8
import time
import json

import redis

class Model(dict):
    _category = "default"
    
    def __init__(self, rd, name):
        self.name = name
        self.hash_key = ":".join((self._category, name))
        self.rd = rd
        
        _data = self.rd.hgetall(self.hash_key)
        _d = _data.copy()
        for _k, _v in _data.items():
            try:
                _value = json.loads(_v)
            except:
                continue
            if isinstance(json.loads(_v), (list, dict)):
                _d[_k] = json.loads(_v)
        dict.__init__(self, **_d)

    @classmethod
    def from_settings(cls, name, settings):
        rd = redis.Redis(host=settings.get("REDIS_HOST"), 
                         port=settings.get("REDIS_PORT"))
        return cls(rd, name)
        
    def __setitem__(self, name, value):
        v = value
        if isinstance(value, (list, dict)):
            value = json.dumps(value)
        self.rd.hset(self.hash_key, name, value)
        dict.__setitem__(self, name, v)

    def __getitem__(self, name):
        dvalue = dict.__getitem__(self, name)
        rvalue = self.rd.hget(self.hash_key, name).decode('utf-8')
        if isinstance(dvalue, (list, dict)):
            if json.dumps(dvalue) != rvalue:
                self[name] = json.loads(rvalue)
            return dict.__getitem__(self, name)
        else:
            return rvalue
        
    def __iter__(self):
        return iter(self.rd.hkeys(self.hash_key))
    
    def __delitem__(self, key):
        self.rd.hdel(self.hash_key, key)
        dict.__delitem__(self, key)

    def update(self, ext, **kwargs):
        if ext:
            for k, v in ext.items():
                self[k] = v
        if kwargs:
            for k, v in kwargs.items():
                self[k] = v
                
    def incr(self, key, interval=1):
        self[key] = self.rd.hincrby(self.hash_key, key, interval)
        return self[key]

    @classmethod
    def filter(cls, rd, **cluster):
        keys = rd.keys("%s:*" % cls._category)
        for key in keys:
            obj = cls(rd, key.split("%s:" % cls._category)[1])
            tag = True
            for k, v in cluster.items():
                if obj.get(k) != v:
                    tag = False
                    break

            if tag:
                yield obj

class Queue(object):
    def __init__(self, rd, key, method="FIFO"):
        self.queue_key = "queue:%s" % key
        self.method = method
        self.rd = rd

    def q_pop(self):
        req = None
        if self.method == 'LIFO':
            req = self.rd.rpop(self.queue_key)
        elif self.method == 'FIFO':
            req = self.rd.lpop(self.queue_key)
        else:
            raise Exception("Dont known how to get item FIFO/LIFO?")

        return req

    def q_mpop(self, num):
        n = num
        while self.q_len() > 0 and n > 0:
            yield self.q_pop()
            n -= 1

    def q_push(self, item):
        self.rd.rpush(self.queue_key, item)

    def q_len(self):
        return int(self.rd.llen(self.queue_key))

    def q_range(self, start=0, end=-1):
        return self.rd.lrange(self.queue_key, start, end)

    def q_flush(self):
        self.rd.delete(self.queue_key)

class Flow(Model, Queue):
    _category = 'flow'

    def __init__(self, rd, name):
        Model.__init__(self, rd, name)
        Queue.__init__(self, rd, name)
    
    def reschedule(self):
        if self.has_key('start_time'):
            del self['start_time']
        self['state'] = 'stopped'
        self.q_flush()

    def reset(self):
        self.q_flush()

    @property
    def domain(self):
        return Domain(self.rd, self['domain'])

    @classmethod
    def reschedule_all(cls, rd):
        flows = cls.filter(rd)
        for f in flows:
            f.reschedule()

    @classmethod
    def reset_all(cls, rd):
        flows = cls.filter(rd)
        for f in flows:
            f.reset()

class Domain(Model, Queue):
    _category = 'spider'

    def __init__(self, rd, name):
        Model.__init__(self, rd, name)
        Queue.__init__(self, rd, name)
    
    def flows(self):
        return Flow.filter(self.rd, domain=self.name)

    @classmethod
    def reset_all(cls, rd):
        spiders = cls.filter(rd)
        for s in spiders:
            s.reset()

    def reset(self):
        #rd.delete(self.hash_key)
        self['scheduled'] = 0
        self.q_flush()
    
class Rule(Model):
    _category = "rule"