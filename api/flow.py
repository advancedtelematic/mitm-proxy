from pathlib import Path
from typing import List, Optional

from .config import Config
from .errors import InvalidFlowName


class FlowName(str):
    """A valid mitmproxy flow name."""
    def __new__(cls, path: Path) -> str:
        if not path.with_suffix(".py").exists:
            raise InvalidFlowName(path.stem)
        return path.stem


class Flow(object):
    """Control the selected mitmproxy flow."""
    config: Config
    running: Optional[FlowName] = None

    def __init__(self, config: Config) -> None:
        self.config = config

    def get_running(self) -> Optional[FlowName]:
        """Return the currently running flow."""
        return self.running

    def set_running(self, name: Optional[FlowName]) -> None:
        """Set the currently running flow."""
        self.running = name

    def available(self) -> List[FlowName]:
        """Return all currently available flows."""
        return [FlowName(path) for path in self.config.flow["root"].glob("*.py")]

    def exists(self, name: str) -> bool:
        """Check if the requested flow name exists."""
        return name in self.available()
