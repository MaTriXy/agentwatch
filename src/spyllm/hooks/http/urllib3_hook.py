# type: ignore
# WARNING: Use httpcore_hook instead!

import logging
from typing import Any, Optional

from urllib3 import HTTPSConnectionPool
from urllib3.connection import HTTPSConnection

from spyllm.hooks.http.http_base_hook import HttpInterceptHook

logger = logging.getLogger(__name__)

class Urllib3Hook(HttpInterceptHook):
    def __init__(self, callback_handler: Any) -> None:
        super().__init__(callback_handler)
        self._original_urlopen: Optional[Any] = None

        raise RuntimeError("Use httpcore_hook")

    def apply_hook(self):
        try:
            import urllib3
        except ImportError:
            logger.debug("urllib3 not installed, skipping hook")
            return
        
        self._original_urlopen = urllib3.connectionpool.HTTPConnectionPool._make_request
        
        # Use a closure to maintain access to both the hook instance and pass through the correct self
        def wrapper(pool_self: HTTPSConnectionPool, conn: HTTPSConnection, method: str, url: str, **kwargs):
            return self._intercepted_make_request(pool_self, conn, method, url, **kwargs)
        
        urllib3.connectionpool.HTTPConnectionPool._make_request = wrapper
        logger.info("urllib3 hook applied")
    
    def _intercepted_make_request(self, pool_self: HTTPSConnectionPool, 
                                  conn: HTTPSConnection, 
                                  method: str, 
                                  url: str, 
                                  headers: dict[str, Any],
                                  body: Optional[str] = None,
                                  **kwargs):
        # Access to the pool's properties
        full_url = f"{pool_self.scheme}://{pool_self.host}:{pool_self.port}{url}"
        logger.info(f"Request intercepted: {method} {full_url}")
        
        # Access to the hook's properties
        # (self here refers to the Urllib3Hook instance)
        
        if 'body' in kwargs and kwargs['body']:
            try:
                body_excerpt = str(kwargs['body'])[:100]
                logger.debug(f"Request body: {body_excerpt}...")
            except:
                logger.debug("Request has body but could not be displayed")
        
        if 'headers' in kwargs:
            logger.debug(f"Request headers: {kwargs['headers']}")
        
        # Process pre-request callbacks
        args, kwargs = self._normalize_request(conn, method, url, **kwargs)
        self.callback_handler.process_pre_request_callbacks(url, method, kwargs.get('headers', {}), kwargs.get('body', None))
        
        # Call the original method with the correct self (pool_self)
        response = self._original_urlopen(pool_self, *args, **kwargs)
    
        # Intercept the response
        logger.info(f"Response received: {response.status}")
        logger.debug(f"Response headers: {response.headers}")
        
        # Process post-request callbacks
        self.callback_handler.process_post_request_callbacks(url, method, response.status, response.headers)
    
        return response
    
    def _normalize_request(self, conn, method, url, **kwargs) -> Any:
        # Handle any normalization you need
        return (conn, method, url), kwargs
    
    def _normalize_response(self, *args: Any, **kwargs: Any) -> Any:
        return args, kwargs
    