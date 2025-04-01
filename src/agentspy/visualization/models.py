from typing import Any

from pydantic import BaseModel

from agentspy.visualization.enums import WebsocketEvent


class WebsocketMessage(BaseModel):
    type: WebsocketEvent
    data: list[dict[str, Any]]