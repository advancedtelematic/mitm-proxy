from typing import Any, Type


class ProxyError(Exception):
    """The base class for proxy errors."""
    pass


class ContentTypeError(ProxyError):
    def __init__(self, expected: str, got: str) -> None:
        self.expected = expected
        self.got = got

    def __str__(self) -> str:
        return f"Expected content-type {self.expected}, got {self.got}"


class DataTypeError(ProxyError):
    def __init__(self, name: str, expected: Type[Any], got: Type[Any]) -> None:
        self.name = name
        self.expected = expected
        self.got = got

    def __str__(self) -> str:
        return f"Expected {self.name} to be of type {self.expected}, got {self.got}"


class MissingFieldError(ProxyError):
    def __init__(self, name: str, field: str) -> None:
        self.name = name
        self.field = field

    def __str__(self) -> str:
        return f"{self.name} missing field: {self.field}"


class UnknownRoleError(ProxyError):
    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return f"unknown role: {self.name}"
