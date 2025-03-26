from datetime import datetime
from typing import Any

from spyllm.enums import HookEventType
from spyllm.models import RemoveNoneBaseModel


class HookEvent(RemoveNoneBaseModel):
    event_type: HookEventType
    timestamp: datetime = datetime.now()
    data: dict[str, Any]