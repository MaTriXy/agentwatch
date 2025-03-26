
from spyllm.client import SpyLLMClient
from spyllm.singleton import Singleton

_singleton = Singleton[SpyLLMClient]()

def initialize() -> SpyLLMClient:
    return _singleton.initialize(SpyLLMClient)

def get_instance() -> SpyLLMClient:
    return _singleton.get_instance()