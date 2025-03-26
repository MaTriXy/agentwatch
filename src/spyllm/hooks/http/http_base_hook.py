import abc
from typing import Any, Optional

from pydantic import BaseModel

from spyllm.hooks.base import BaseHook, HookCallbackProto


class HttpInterceptRule(BaseModel):
    host: str
    port: Optional[int] = None

class HttpInterceptHook(BaseHook):
    def __init__(self, callback_handler: HookCallbackProto) -> None:
        super().__init__(callback_handler)
        self._rules: list[HttpInterceptRule] = []
    
    def add_intercept_rule(self, host: str, port: Optional[int] = None) -> None:
        rule = HttpInterceptRule(host=host, port=port)
        self._rules.append(rule)

    def should_intercept(self, 
                         host: str, 
                         port: Optional[int] = None, 
                         path: str = "/", 
                         scheme: str = "https", 
                         **kwargs: Any) -> bool:
        for rule in self._rules:
            if rule.host == host and (rule.port is None or rule.port == port):
                return True
        return False
    
    @abc.abstractmethod
    def _normalize_request(self, *args: Any, **kwargs: Any) -> Any:
        ...
    
    @abc.abstractmethod
    def _normalize_response(self, *args: Any, **kwargs: Any) -> Any:
        ...