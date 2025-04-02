import logging
from typing import Any, Optional

from agentwatch.enums import HookEventType
from agentwatch.hooks.http.http_base_hook import HttpInterceptHook
from agentwatch.hooks.http.models import HTTPRequestData, HTTPResponseData
from agentwatch.hooks.models import HookEvent

try:
    import httpcore
    import httpx
except ImportError:
    pass

logger = logging.getLogger(__name__)

class HttpcoreHook(HttpInterceptHook):
    def __init__(self, callback_handler: Any) -> None:
        super().__init__(callback_handler)
        self._original_handle_request: Optional[Any] = None
        self._original_handle_async_request: Optional[Any] = None
    
    def apply_hook(self) -> None:
        try:
            import httpcore
        except ImportError:
            logger.debug("httpcore not installed, skipping hook")
            return
        
        self._original_handle_request = httpcore.HTTPConnection.handle_request
        
        def sync_wrapper(conn_self: httpcore.HTTPConnection, request: httpcore.Request) -> httpcore.Response:
            return self._intercepted_handle_request(conn_self,request)
        
        httpcore.HTTPConnection.handle_request = sync_wrapper  # type: ignore
        
        # Async version (if available)
        if hasattr(httpcore, 'AsyncHTTPConnection'):
            self._original_handle_async_request = httpcore.AsyncHTTPConnection.handle_async_request
            
            async def async_wrapper(conn_self: httpcore.AsyncHTTPConnection, request: httpcore.Request) -> httpcore.Response:
                return await self._intercepted_handle_async_request(conn_self, request)
            
            httpcore.AsyncHTTPConnection.handle_async_request = async_wrapper  # type: ignore
        
        logger.debug("httpcore hook applied")
    
    def _normalize_request(self, request: httpcore.Request) -> HookEvent:
        # Convert to httpx.Request
        httpx_request = httpx.Request(
            method=request.method.decode('ascii'),
            url=str(request.url),
            headers=[(k.decode('ascii'), v.decode('ascii')) for k, v in request.headers],
            content=b"".join(request.stream).decode()  # type: ignore
        )
                
        request_data = HTTPRequestData(
            method=httpx_request.method,
            url=str(httpx_request.url),
            headers=dict(httpx_request.headers),
            body=httpx_request.content.decode()
        )
        
        return HookEvent(
            event_type=HookEventType.HTTP_REQUEST,
            data=request_data.model_dump()
        )

    def _normalize_response(self, response: httpcore.Response) -> HookEvent:
        httpx_response = httpx.Response(
            status_code=response.status,
            headers=response.headers,
            content=response.read(),
            extensions=response.extensions,
        )

        response_data = HTTPResponseData(
            status_code=httpx_response.status_code,
            headers=dict(httpx_response.headers),
            body=httpx_response.text
        )
        
        return HookEvent(
            event_type=HookEventType.HTTP_RESPONSE,
            data=response_data.model_dump()
        )
    
    def _request_callback_sync(self, request: httpcore.Request) -> None:
        normalized = self._normalize_request(request)
        self._callback_handler.on_hook_callback_sync(self, normalized)
    
    def _response_callback_sync(self, response: httpcore.Response) -> None:
        normalized = self._normalize_response(response) 
        self._callback_handler.on_hook_callback_sync(self, normalized)
    
    async def _request_callback(self, request: httpcore.Request) -> None:
        normalized = self._normalize_request(request)
        await self._callback_handler.on_hook_callback(self, normalized)
    
    async def _response_callback(self, response: httpcore.Response) -> None:
        normalized = self._normalize_response(response) 
        await self._callback_handler.on_hook_callback(self, normalized)

    def _intercepted_handle_request(self, conn_self: httpcore.HTTPConnection, request: httpcore.Request) -> httpcore.Response:
        self._request_callback_sync(request)
        response: httpcore.Response = self._original_handle_request(conn_self, request)  # type: ignore
        self._response_callback_sync(response)

        # Since we messed up the response, we'll need to create a new one
        new_response = httpcore.Response(
            status=response.status,
            headers=response.headers,
            content=response.read(),
            extensions=response.extensions.copy() if response.extensions else {},  # type: ignore
        )

        return new_response
    
    async def _intercepted_handle_async_request(self, conn_self: httpcore.AsyncHTTPConnection, request: httpcore.Request) -> httpcore.Response:
        await self._request_callback(request)
        response: httpcore.Response = self._original_handle_async_request(conn_self, request)  # type: ignore
        await self._response_callback(response)

        # Since we messed up the response, we'll need to create a new one
        new_response = httpcore.Response(
            status=response.status,
            headers=response.headers,
            content=response.read(),
            extensions=response.extensions.copy() if response.extensions else {},  # type: ignore
        )

        return new_response
    
    def remove_hook(self) -> None:
        """Remove the hook and restore original functions"""
        try:
            import httpcore
            if self._original_handle_request:
                httpcore.HTTPConnection.handle_request = self._original_handle_request  # type: ignore
            
            if self._original_handle_async_request and hasattr(httpcore, 'AsyncHTTPConnection'):
                httpcore.AsyncHTTPConnection.handle_async_request = self._original_handle_async_request  # type: ignore
            
            logger.debug("httpcore hook removed")
        except ImportError:
            pass