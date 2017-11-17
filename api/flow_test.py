from pathlib import Path

from .config import Config
from .flow import Flow, FlowPath


FLOWS = Path.cwd() / "fixtures/flows"

def new_config() -> Config:
    return Config({
        "http.host": "127.0.0.1",
        "http.port": 1234,
        "flow.root": "fixtures/flows",
        "flow.initial": "foo",
        "mitm.cadir": "<unused>",
        "mitm.client_certs": "<unused>",
        "mitm.upstream_trusted_ca": "<unused>",
    })

def test_flows() -> None:
    flow = Flow(new_config())
    assert flow.get_running() is None
    assert flow.config.flow["initial"] == "foo"

    assert flow.available() == ["bar", "foo"]
    assert flow.find("foo") is not None
    assert flow.find("xfoo") is None

    flow._set_running(FlowPath(FLOWS / "bar"))
    assert flow.get_running() == "bar"
