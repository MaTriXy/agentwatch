# type: ignore
# WARNING: Use httpcore_hook instead!

import logging
from typing import Any

from spyllm.hooks.http.http_base_hook import HttpInterceptHook

logger = logging.getLogger(__name__)

class RequestsHook(HttpInterceptHook):
    def __init__(self, callback_handler: Any) -> None:
        super().__init__(callback_handler)

        raise RuntimeError("Use httpcore_hook")

    def apply_hook(self):
        try:
            import requests
            from requests.adapters import HTTPAdapter
        except ImportError:
            logger.debug("urllib3 not installed, skipping hook")
            return
        
        class InterceptHTTPAdapter(HTTPAdapter):
            def __init__(self, pool_connections = 10, pool_maxsize = 10, max_retries = 0, pool_block = False):
                super().__init__(pool_connections, pool_maxsize, max_retries, pool_block)

            def send(self, request, **kwargs):
                """Intercept and log request before sending."""
                
                if request.body:
                    logger.debug(f"Request body: {request.body[:100]}...")
                
                # Send the request using the parent method
                response = super().send(request, **kwargs)
            
                
                return response
            
        s = requests.Session()
        adapter = InterceptHTTPAdapter()
        s.mount('https://', adapter)
        s.mount('http://', adapter)
        
        logger.info("requests hook applied")
    
    def _normalize_request(self, *args: Any, **kwargs: Any) -> Any:
        return args, kwargs
    
    def _normalize_response(self, *args: Any, **kwargs: Any) -> Any:
        return args, kwargs
    



        


