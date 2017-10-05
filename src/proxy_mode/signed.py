from mitmproxy.http import HTTPFlow
from proxy_mode.proxy_mode import ProxyMode


class AlterSigned(ProxyMode):
    """AlterSigned will mutate the signed section of the TUF metadata."""
    def __init__(self) -> None:
        super(AlterSigned, self).__init__("AlterSigned")

    @classmethod
    def request(cls, flow: HTTPFlow) -> None:
        raise NotImplementedError()

    @classmethod
    def response(cls, flow: HTTPFlow) -> None:
        raise NotImplementedError()
