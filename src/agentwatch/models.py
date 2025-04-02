import time
import uuid
from typing import Any, Optional

from pydantic import BaseModel, Field

from agentwatch.enums import CommandAction


class RemoveNoneBaseModel(BaseModel):
    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """
        This Overrides the default model dump method to exclude None values
        """
        return super().model_dump(exclude_none=True)

class Command(RemoveNoneBaseModel):
    """Command class for IPC communication"""
    action: CommandAction
    params: dict[str, Any] = Field(default_factory=dict)
    callback_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    execution_id: str
    timestamp: float = Field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()

    @classmethod
    def from_dict(cls, execution_id: str, action: CommandAction, params: Optional[dict[str, Any]] = None) -> "Command":
        return cls(
            execution_id=execution_id,
            action=action,
            params=params or {}
        )

    def __str__(self) -> str:
        return f"Command({self.action}, params={self.params}, callback_id={self.callback_id})"


class CommandResponse(RemoveNoneBaseModel):
    """Response class for IPC communication"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    callback_id: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CommandResponse":
        return cls(**data)

    def __str__(self) -> str:
        return f"Response({self.model_dump()})"
    