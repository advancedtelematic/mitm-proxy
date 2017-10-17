from mitmproxy.http import HTTPFlow


class AbstractMode(object):
    """The base class for all proxy processing modes."""
    def __init__(self, name: str) -> None:
        self.name = name

    def request(self, flow: HTTPFlow) -> None:
        raise NotImplementedError()

    def requestheaders(self, flow: HTTPFlow) -> None:
        raise NotImplementedError()

    def response(self, flow: HTTPFlow) -> None:
        flow.response.headers['x-tuf-mitm-proxy'] = 'true'
        raise NotImplementedError()

    def responseheaders(self, flow: HTTPFlow) -> None:
        raise NotImplementedError()
