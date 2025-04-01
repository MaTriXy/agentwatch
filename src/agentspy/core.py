
from agentspy.client import AgentspyClient
from agentspy.singleton import Singleton

_singleton = Singleton[AgentspyClient]()

def initialize() -> AgentspyClient:
    return _singleton.initialize(AgentspyClient)

def get_instance() -> AgentspyClient:
    return _singleton.get_instance()

def set_verbose() -> None:
    _singleton.get_instance().set_verbose()