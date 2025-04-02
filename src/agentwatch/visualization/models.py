from typing import Any

from pydantic import BaseModel

from agentwatch.visualization.enums import WebsocketEvent


class WebsocketMessage(BaseModel):
    type: WebsocketEvent
    data: list[dict[str, Any]]