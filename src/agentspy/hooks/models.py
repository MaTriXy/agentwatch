from datetime import datetime
from typing import Any

from agentspy.enums import HookEventType
from agentspy.models import RemoveNoneBaseModel


class HookEvent(RemoveNoneBaseModel):
    event_type: HookEventType
    timestamp: datetime = datetime.now()
    data: dict[str, Any]