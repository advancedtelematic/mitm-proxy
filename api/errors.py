from pathlib import Path


class Error(Exception):
    """The base class for proxy errors."""
    pass

class InvalidFlowPath(Error):
    def __init__(self, path: Path) -> None:
        self.path = path

    def __str__(self) -> str:
        return f"Flow path not found: {self.path}"

class InvalidFlowRoot(Error):
    def __init__(self, root: str) -> None:
        self.root = root

    def __str__(self) -> str:
        return f"Root directory not found: {self.root}"

class InvalidKeyId(Error):
    def __init__(self, keyid: str) -> None:
        self.keyid = keyid

    def __str__(self) -> str:
        return f"Invalid keyid: {self.keyid}"

class MissingField(Error):
    def __init__(self, name: str, field: str) -> None:
        self.name = name
        self.field = field

    def __str__(self) -> str:
        return f"{self.name} missing field: {self.field}"

class StillRunning(Error):
    def __init__(self, pid: int) -> None:
        self.pid = pid

    def __str__(self) -> str:
        return f"Process ID already running: {self.pid}"

class UnknownRole(Error):
    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return f"unknown role: {self.name}"
