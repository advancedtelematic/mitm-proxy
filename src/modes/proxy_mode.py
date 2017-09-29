import sys

class ProxyMode(object):
    def __init__(self, name):
        self.name = name

    def setup(self):
        pass

    def cleanup(self):
        pass

    def request(self, flow):
        pass

    def requestheaders(self, flow):
        pass

    def response(self, flow):
        pass

    def responseheaders(self, flow):
        pass
