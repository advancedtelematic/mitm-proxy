from mitmproxy.http import HTTPFlow
from typing import List


class Modifier(object):
    """The base class for modifiers."""
    subclasses: List = []

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.subclasses.append(cls)

    def request(self, flow: HTTPFlow) -> None:
        raise NotImplementedError()

    def requestheaders(self, flow: HTTPFlow) -> None:
        raise NotImplementedError()

    def response(self, flow: HTTPFlow) -> None:
        raise NotImplementedError()

    def responseheaders(self, flow: HTTPFlow) -> None:
        raise NotImplementedError()


class Duplicate(Modifier):
    """Duplicate incoming requests."""

    def __init__(self) -> None:
        pass

    @classmethod
    def request(cls, flow: HTTPFlow) -> None:
        # dup = flow.copy()
        # ctx.master.view.add(dup)
        # ctx.master.replay_request(dup, block=True)
        pass
