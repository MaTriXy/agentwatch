
from agentwatch.client import AgentwatchClient
from agentwatch.singleton import Singleton

_singleton = Singleton[AgentwatchClient]()

def initialize() -> AgentwatchClient:
    return _singleton.initialize(AgentwatchClient)

def get_instance() -> AgentwatchClient:
    return _singleton.get_instance()

def set_verbose() -> None:
    _singleton.get_instance().set_verbose()