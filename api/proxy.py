import logging as log
import shlex

from subprocess import Popen
from typing import List, Optional

from .config import Config
from .flow import Flow, FlowPath


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
            self.start(FlowPath(self.config.flow["root"] / initial))

    def start(self, path: FlowPath) -> None:
        """Start the given mitmproxy flow."""
        self.stop()
        self.process = Popen(self._args(path))
        self.flow._set_running(path)
        log.debug(f"started mitmproxy pid: {self.process.pid}")

    def stop(self) -> None:
        """Stop any currently running child process."""
        if self.process is None:
            return
        elif self.process.poll() is None:
            log.debug(f"stopping mitmproxy pid: {self.process.pid}")
            self.process.kill()

        log.debug(f"mitmproxy pid {self.process.pid} exit code: {self.process.returncode}")
        self.process = None
        self.flow._set_running(None)

    def _args(self, path: FlowPath, cmd: str="mitmdump") -> List[str]:
        """Return the command line arguments used to start mitmproxy."""
        cmd = f"""pipenv run {cmd}
        --transparent
        --host
        --script="{path}"
        --cadir={self.config.mitm["cadir"]}
        --upstream-trusted-ca="{self.config.mitm["upstream_trusted_ca"]}"
        --client-certs="{self.config.mitm["client_certs"]}"
        """
        return shlex.split(cmd)
