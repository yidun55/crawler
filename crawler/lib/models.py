# coding: utf-8
import json

import redis


class RedisBindMetaClass(type):
    def __new__(cls, name, extends, attrs):
        attrs['redis'] = redis.Redis()
        return super(RedisBindMetaClass, cls).__new__(cls, name, extends, attrs)

__metaclass__ = RedisBindMetaClass


class Model(dict):
    _category = "default"

    def __init__(self, name):
        self.name = name
        self.hash_key = ":".join((self._category, name))

        _data = self.redis.hgetall(self.hash_key)
        _d = _data.copy()
        for _k, _v in _data.items():
            try:
                _value = json.loads(_v)
            except:
                continue
            if isinstance(_value, (list, dict)):
                _d[_k] = _value
        dict.__init__(self, **_d)

    def __setitem__(self, name, value):
        v = value
        if isinstance(value, (list, dict)):
            value = json.dumps(value)
        self.redis.hset(self.hash_key, name, value)
        dict.__setitem__(self, name, v)

    def __getitem__(self, name):
        dvalue = dict.__getitem__(self, name)
        rvalue = self.redis.hget(self.hash_key, name).decode('utf-8')
        if isinstance(dvalue, (list, dict)):
            if json.dumps(dvalue) != rvalue:
                self[name] = json.loads(rvalue)
            return dict.__getitem__(self, name)
        else:
            return rvalue

    def __iter__(self):
        return iter(self.redis.hkeys(self.hash_key))

    def __delitem__(self, key):
        self.redis.hdel(self.hash_key, key)
        dict.__delitem__(self, key)

    def update(self, ext, **kwargs):
        if ext:
            for k, v in ext.items():
                self[k] = v
        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def incr(self, key, interval=1):
        self[key] = self.redis.hincrby(self.hash_key, key, interval)
        return self[key]

    @classmethod
    def filter(cls, **cluster):
        keys = cls.redis.keys("%s:*" % cls._category)
        for key in keys:
            obj = cls(cls.redis, key.split("%s:" % cls._category)[1])
            tag = True
            for k, v in cluster.items():
                if obj.get(k) != v:
                    tag = False
                    break

            if tag:
                yield obj


class Queue(object):
    def __init__(self, key, method="FIFO"):
        self.queue_key = "queue:%s" % key
        self.method = method

    def q_pop(self):
        req = None
        if self.method == 'LIFO':
            req = self.redis.rpop(self.queue_key)
        elif self.method == 'FIFO':
            req = self.redis.lpop(self.queue_key)
        else:
            raise Exception("Dont known how to get item FIFO/LIFO?")

        return req

    def q_mpop(self, num):
        n = num
        while self.q_len() > 0 and n > 0:
            yield self.q_pop()
            n -= 1

    def q_push(self, item):
        self.redis.rpush(self.queue_key, item)

    def q_len(self):
        return int(self.redis.llen(self.queue_key))

    def q_range(self, start=0, end=-1):
        return self.redis.lrange(self.queue_key, start, end)

    def q_flush(self):
        self.redis.delete(self.queue_key)


class Flow(Model, Queue):
    _category = 'flow'

    def reschedule(self):
        if "start_time" in self.has_key:
            del self['start_time']
        self['state'] = 'stopped'
        self.q_flush()

    def reset(self):
        self.q_flush()

    @property
    def domain(self):
        return Domain(self.redis, self['domain'])

    @classmethod
    def reschedule_all(cls):
        flows = cls.filter()
        for f in flows:
            f.reschedule()

    @classmethod
    def reset_all(cls):
        flows = cls.filter()
        for f in flows:
            f.reset()


class Domain(Model, Queue):
    _category = 'spider'

    def flows(self):
        return Flow.filter(self.redis, domain=self.name)

    @classmethod
    def reset_all(cls):
        spiders = cls.filter()
        for s in spiders:
            s.reset()

    def reset(self):
        self['scheduled'] = 0
        self.q_flush()


class Rule(Model):
    _category = "rule"
