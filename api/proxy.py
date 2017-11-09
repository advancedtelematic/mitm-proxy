import logging
import shlex

from subprocess import Popen
from typing import List, Optional

from .config import Config
from .flow import Flow, FlowName


log = logging.getLogger(__name__)

class Proxy(object):
    """Controller for spawning instances of mitmproxy."""
    flow: Flow
    config: Config
    process: Optional[Popen] = None

    def __init__(self, flow: Flow) -> None:
        self.flow = flow
        self.config = flow.config

        initial = self.config.flow["initial"]
        if initial:
            self.start(FlowName(self.config.flow["root"] / initial))

    def start(self, name: FlowName) -> None:
        """Start the given mitmproxy flow."""
        self.stop()
        self.process = Popen(self._args(name))
        self.flow.set_running(name)
        log.debug(f"started pid: {self.process.pid}")

    def stop(self) -> None:
        """Stop any currently running child process."""
        if self.process is None:
            return
        elif self.process.poll() is None:
            log.debug(f"stopping pid: {self.process.pid}")
            self.process.kill()

        log.debug(f"pid {self.process.pid} exited with {self.process.returncode}")
        self.process = None
        self.flow.set_running(None)

    def _args(self, name: FlowName, cmd: str="mitmdump") -> List[str]:
        """Return the command line arguments used to start mitmproxy."""
        cmd = f"""pipenv run {cmd}
        --transparent
        --host
        --script="{(self.config.flow["root"] / name).with_suffix(".py")}"
        --cadir={self.config.mitm["cadir"]}
        --upstream-trusted-ca="{self.config.mitm["upstream_trusted_ca"]}"
        --client-certs="{self.config.mitm["client_certs"]}"
        """
        return shlex.split(cmd)
