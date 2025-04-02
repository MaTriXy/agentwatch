from datetime import datetime
from typing import Any

from agentwatch.enums import HookEventType
from agentwatch.models import RemoveNoneBaseModel


class HookEvent(RemoveNoneBaseModel):
    event_type: HookEventType
    timestamp: datetime = datetime.now()
    data: dict[str, Any]