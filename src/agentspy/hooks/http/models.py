
from typing import Any, Optional

from pydantic import BaseModel


class HTTPRequestData(BaseModel):
    method: str
    url: str
    headers: dict[str, str]
    body: Optional[str] = None

class HTTPResponseData(BaseModel):
    status_code: int
    headers: dict[str, str]
    body: Optional[str] = None
    request: dict[str, Any] = {}
