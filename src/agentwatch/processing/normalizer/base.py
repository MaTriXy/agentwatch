import abc
from typing import Any


class BaseHTTPContentNormalizer:
    def __init__(self) -> None:
        self._supported_content_types: list[str] = []

    @property
    def supported_content_types(self) -> list[str]:
        return self._supported_content_types

    @abc.abstractmethod
    def normalize(self, content: str) -> str:
        """Normalize the content"""
        ...
