import threading
from typing import Any, Callable, Generic, Optional, TypeVar, cast

T = TypeVar('T')

class Singleton(Generic[T]):
    _instance: Optional[T] = None
    _sync_lock = threading.Lock()
    _initialized = False
    
    @classmethod
    def get_instance(cls) -> T:
        """Synchronous access to the singleton instance"""
        with cls._sync_lock:
            if cls._instance is None or not cls._initialized:
                raise RuntimeError(
                    "Singleton not initialized. Call initialize() or await initialize_async() first"
                )
            return cast(T, cls._instance)
    
    @classmethod
    def initialize(cls, factory: Callable[[], T], *args: Any, **kwargs: Any) -> T:
        """Initialize the singleton synchronously"""
        with cls._sync_lock:
            if cls._instance is None or not cls._initialized:
                cls._instance = factory(*args, **kwargs)
                cls._initialized = True
            return cast(T, cls._instance)
    
    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (mainly for testing)"""
        with cls._sync_lock:
            cls._instance = None
            cls._initialized = False