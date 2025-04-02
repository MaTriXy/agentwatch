from unittest.mock import AsyncMock, Mock

import pytest
from httpcore import Request, Response

from agentwatch.enums import HookEventType
from agentwatch.hooks.http.httpcore_hook import HttpcoreHook
from agentwatch.hooks.models import HookEvent


@pytest.fixture
def callback_handler():
    handler = Mock()
    handler.on_hook_callback_sync = Mock()
    handler.on_hook_callback = AsyncMock()
    return handler

@pytest.fixture
def httpcore_hook(callback_handler):
    hook = HttpcoreHook(callback_handler)
    return hook

def test_init(callback_handler):
    hook = HttpcoreHook(callback_handler)
    assert hook._callback_handler == callback_handler

def test_request_callback_sync(httpcore_hook, callback_handler):
    request = Request(b"GET", "https://api.example.com")
    request.headers = [(b"Content-Type", b"application/json")]
    expected_event = httpcore_hook._normalize_request(request)
    
    httpcore_hook._request_callback_sync(request)
    
    callback_handler.on_hook_callback_sync.assert_called_once_with(
        httpcore_hook, 
        expected_event
    )

def test_response_callback_sync(httpcore_hook, callback_handler):
    request = Request(b"GET", "https://api.example.com")
    request.headers = [(b"Content-Type", b"application/json")]
    response = Response(200)
    response.headers = [(b"Content-Type", b"application/json")]
    expected_event = httpcore_hook._normalize_response(response)
    
    httpcore_hook._response_callback_sync(response)
    
    callback_handler.on_hook_callback_sync.assert_called_once_with(
        httpcore_hook, 
        expected_event
    )

@pytest.mark.asyncio
async def test_request_callback(httpcore_hook, callback_handler):
    request = Request("GET", "https://api.example.com")
    expected_event = httpcore_hook._normalize_request(request)
    
    await httpcore_hook._request_callback(request)
    
    callback_handler.on_hook_callback.assert_awaited_once_with(
        httpcore_hook, 
        expected_event
    )

@pytest.mark.asyncio
async def test_response_callback(httpcore_hook, callback_handler):
    response = Response(200)
    expected_event = httpcore_hook._normalize_response(response)
    
    await httpcore_hook._response_callback(response)
    
    callback_handler.on_hook_callback.assert_awaited_once_with(
        httpcore_hook, 
        expected_event
    )