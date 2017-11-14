import logging as log

from pathlib import Path
from typing import List, Optional

from .config import Config
from .errors import InvalidFlowPath


class FlowPath(Path):
    """A valid mitmproxy flow path."""
    def __new__(cls, path: Path) -> Path:
        path = path.with_suffix(".py")
        if not path.exists():
            raise InvalidFlowPath(path)
        return path

class Flow(object):
    """Control the selected mitmproxy flow."""
    config: Config
    running: Optional[FlowPath] = None

    def __init__(self, config: Config) -> None:
        self.config = config

    def find(self, name: str) -> Optional[FlowPath]:
        """Return the flow if it exists."""
        try:
            return FlowPath(self.config.flow["root"] / name)
        except InvalidFlowPath:
            log.error(f"flow not found: {name}")
            return None

    def available(self) -> List[str]:
        """Return all currently available flows."""
        return [FlowPath(path).stem for path in self.config.flow["root"].glob("*.py")]

    def get_running(self) -> Optional[str]:
        """Return the currently running flow."""
        if self.running:
            return self.running.stem
        else:
            return None

    def _set_running(self, path: Optional[FlowPath]) -> None:
        """Internal method to set the currently running flow."""
        log.debug(f"setting flow path: {path}")
        self.running = path
