from .abstract import AbstractMode
from mitmproxy.http import HTTPFlow


class AlterSigned(AbstractMode):
    """AlterSigned will mutate the signed section of the TUF metadata."""
    def __init__(self) -> None:
        super(AlterSigned, self).__init__("AlterSigned")

    @classmethod
    def request(cls, flow: HTTPFlow) -> None:
        raise NotImplementedError()

    @classmethod
    def response(cls, flow: HTTPFlow) -> None:
        raise NotImplementedError()
