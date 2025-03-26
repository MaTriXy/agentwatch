from enum import Enum


class CommandAction(Enum):
    EVENT = "event"
    SHUTDOWN = "shutdown"
    PING = "ping"
    ADD_WEBHOOK = "add_webhook"
    VERBOSE = "verbose"
    
class HookEventType(Enum):
    HTTP_REQUEST = "http_request"
    HTTP_RESPONSE = "http_response"
