__author__ = 'KMihajlov'

class DynamicParameters(object):
    def __init__(self, request):
        self.request = request
    def __getattr__(self, name):
        return self.request.get(name)
    def get(self, name , default=None):
        return self.request.get(name, default)