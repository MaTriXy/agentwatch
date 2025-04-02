import abc
from typing import Any, Protocol


class BaseHook():
    def __init__(self, callback_handler: 'HookCallbackProto'):
        self._callback_handler = callback_handler
        self._hooked = False

    @abc.abstractmethod
    def apply_hook(self) -> None:
        ...

    @abc.abstractmethod
    def should_intercept(self, *args: Any, **kwargs: Any) -> bool:
        ...

class HookCallbackProto(Protocol):
    def on_hook_callback_sync(self, hook: BaseHook, obj: Any) -> None: ...
    async def on_hook_callback(self, hook: BaseHook, obj: Any) -> None: ...
