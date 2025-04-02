from abc import ABC, abstractmethod
from typing import Any, Optional

from agentwatch.enums import HookEventType
from agentwatch.graph.graph import GraphStructure


class BaseProcessor(ABC):
    def __init__(self) -> None:
        self._supported_events: list[HookEventType] = []

    @property
    def supported_events(self) -> list[HookEventType]:
        return self._supported_events

    @abstractmethod
    async def process(self, event_type: HookEventType, data: dict[str, Any]) -> Optional[GraphStructure]:
        """Process the event data and return processed result"""
        ...

    @abstractmethod
    def _parse_nodes_and_edges(*args: Any, **kwargs: Any) -> Optional[GraphStructure]:
        """Create nodes and edges from the data
        Returns:
            tuple[list[Node], list[Edge]]: Tuple containing list of nodes and edges
        """
        ...

    def can_handle(self, event_type: HookEventType) -> bool:
        return event_type in self._supported_events