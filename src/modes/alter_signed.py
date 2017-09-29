from mitmproxy import ctx
from mitmproxy.models import decoded
from mitmplugin import MITMPlugin

class AlterSigned(ProxyMode):
    def __init__(self):
        super(AlterSigned, self).__init__("alter-signed")

    def response(self, flow):
        pass

def start():
    return AlterSigned()
