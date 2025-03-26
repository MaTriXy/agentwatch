# type: ignore
import logging
from functools import wraps
from typing import Any, Callable, Coroutine

from httpx import Request, Response

from spyllm.enums import HookEventType
from spyllm.hooks.http.http_base_hook import HttpInterceptHook
from spyllm.hooks.http.models import HTTPRequestData, HTTPResponseData
from spyllm.hooks.models import HookEvent

logger = logging.getLogger(__name__)

class HttpxHook(HttpInterceptHook):
    def __init__(self, callback_handler: Any) -> None:
        super().__init__(callback_handler)

        raise RuntimeError("Use httpx_core")
    
    def _normalize_request(self, request: Request) -> HookEvent:
        request_data = HTTPRequestData(
            method=request.method,
            url=str(request.url),
            headers=dict(request.headers),
            body=request.content.decode() if request.content else None
        )
        
        return HookEvent(
            event_type=HookEventType.HTTP_REQUEST,
            data=request_data.model_dump()
        )

    def _normalize_response(self, response: Response) -> HookEvent:
        response_data = HTTPResponseData(
            status_code=response.status_code,
            headers=dict(response.headers),
            body=response.read().decode(),
            request=self._normalize_request(response.request).data
        )
        
        return HookEvent(
            event_type=HookEventType.HTTP_RESPONSE,
            data=response_data.model_dump()
        )
    
    def _request_callback_sync(self, request: Request) -> None:
        logger.debug(f"Request: {request}")
        normalized = self._normalize_request(request)
        self._callback_handler.on_hook_callback_sync(self, normalized)
    
    def _response_callback_sync(self, response: Response) -> None:
        logger.debug(f"Response: {response}")
        normalized = self._normalize_response(response) 
        self._callback_handler.on_hook_callback_sync(self, normalized)
    
    async def _request_callback(self, request: Request) -> None:
        logger.debug(f"Request: {request}")
        normalized = self._normalize_request(request)
        await self._callback_handler.on_hook_callback(self, normalized)
    
    async def _response_callback(self, response: Response) -> None:
        logger.debug(f"Response: {response}")
        normalized = self._normalize_response(response) 
        await self._callback_handler.on_hook_callback(self, normalized)
    
    def apply_hook(self) -> None:
        try:
            import httpx
            from httpx import AsyncHTTPTransport, HTTPTransport
        except ImportError:
            logger.info("httpx not installed, skipping hook")
            return
        
        logger.debug("Applying httpx hook")
        
        p_self = self

        try:
            class InterceptTransportSync(HTTPTransport):
                def __init__(self, *args: Any, **kwargs: Any):
                    super().__init__(*args, **kwargs)
                    self._event_hooks: dict[str, list[Callable[[Any], Any]]] = {
                        "request": [p_self._request_callback_sync],
                        "response": [p_self._response_callback_sync]
                    }
                
                def handle_request(self, request: Request) -> Any:
                    # Apply request hooks
                    url = request.url
                    should_intercept = p_self.should_intercept(url.host, url.port, url.path, url.scheme)
                
                    if should_intercept:
                        for hook in self._event_hooks.get("request", []):
                            hook(request)
                    
                    # Get the response using the parent class
                    response: Response = super().handle_request(request)
                    response.request = request

                    # Apply response hooks
                    if should_intercept:
                        for hook in self._event_hooks.get("response", []):
                            hook(response)
                        
                    return response

            # For async applications
            class InterceptTransport(AsyncHTTPTransport):
                def __init__(self, *args: Any, **kwargs: Any):
                    super().__init__(*args, **kwargs)
                    self._event_hooks: dict[str, list[Callable[[Any], Coroutine[Any, Any, Any]]]] = {
                        "request": [p_self._request_callback],
                        "response": [p_self._response_callback]
                    }
                
                async def handle_async_request(self, request: Request) -> Any:
                    # Apply request hooks
                    url = request.url
                    should_intercept = p_self.should_intercept(url.host, url.port, url.path, url.scheme)
                    
                    if should_intercept:
                        for hook in self._event_hooks.get("request", []):
                            await hook(request)
                    
                    # Get the response using the parent class
                    response: Response = await super().handle_async_request(request)
                    response.request = request

                    # Apply response hooks
                    if should_intercept:
                        for hook in self._event_hooks.get("response", []):
                            await hook(response)
                        
                    return response
            
            # Store original methods
            setattr(httpx.Client, "__original_init__", httpx.Client.__init__)
            setattr(httpx.AsyncClient, "__original_init__", httpx.AsyncClient.__init__)
            
            original_client_init = httpx.Client.__init__
            original_async_client_init = httpx.AsyncClient.__init__

            @wraps(original_client_init)
            def patched_client_init(client_self, *args: Any, **kwargs: Any) -> Any:  # type: ignore
                kwargs['transport'] = InterceptTransportSync()
                return original_client_init(client_self, *args, **kwargs)
            
            @wraps(original_async_client_init)
            def patched_async_client_init(client_self, *args: Any, **kwargs: Any) -> Any:  # type: ignore
                kwargs['transport'] = InterceptTransport()
                return original_async_client_init(client_self, *args, **kwargs)
            
            # Apply the patches
            httpx.Client.__init__ = patched_client_init  # type: ignore
            httpx.AsyncClient.__init__ = patched_async_client_init  # type: ignore
        except Exception as e:
            logger.error(f"Error applying httpx hook: {e}")
            return

        logger.debug("httpx hook applied")
        self._hooked = True