import json

from jsonpath import jsonpath as jpath

class JsonPathSelector(object):
    def __init__(self, response=None, custom_body=None):
        self.body = ""
        if response:
            self.body = response.body
        if custom_body:
            self.body = custom_body

    def jpath(self, query):
        jobject = json.loads(self.body)
        result = jpath(jobject, query)

        if type(result) is not list:
            result = [result]

        return result
