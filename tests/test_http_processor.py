
import uuid

import pytest

from agentspy.enums import HookEventType
from agentspy.graph.consts import APP_NODE_ID
from agentspy.graph.models import LLMNode, ModelGenerateEdge, ToolCallEdge, ToolNode
from agentspy.llm.anthropic_models import AnthropicRequestModel, AnthropicResponseModel
from agentspy.llm.enums import Role
from agentspy.llm.models import AssistantMessage, TextContent, Tool, ToolUse, UserMessage
from agentspy.processing.http_processing import HttpProcessor


@pytest.fixture
def http_processor():
    return HttpProcessor()

@pytest.fixture
def sample_message_request():
    return AnthropicRequestModel(
        model="gpt-4",
        messages=[
            UserMessage(content="Hello"),
            AssistantMessage(content=[
                ToolUse(name="calculator", input={"nums": "1+1"}, id=uuid.uuid4().hex),
                TextContent(text="The answer is 2")
            ])
        ],
        tools=[Tool(name="calculator", description="Performs calculations", input_schema={"nums": "str"})]
    )

@pytest.fixture
def sample_message_response():
    return AnthropicResponseModel(
        id=uuid.uuid4().hex,
        role=Role.ASSISTANT,
        type="message",
        stop_reason="tool_use",
        model="gpt-4",
        content=[
            TextContent(text="Hello there"),
            ToolUse(name="search", input={"keyword": "python"}, id=uuid.uuid4().hex)
        ]
    )

def test_init(http_processor):
    assert http_processor._supported_events == [
        HookEventType.HTTP_REQUEST,
        HookEventType.HTTP_RESPONSE
    ]

@pytest.mark.asyncio
async def test_process_http_request(http_processor, sample_message_request):
    request_data = {
        "method": "POST",
        "url": "http://test.com",
        "headers": {},
        "body": sample_message_request.model_dump_json()
    }
    
    result = await http_processor.process(
        HookEventType.HTTP_REQUEST, 
        request_data
    )
    
    assert result is not None
    nodes, edges = result
    assert any(isinstance(node, LLMNode) for node in nodes)
    assert any(isinstance(node, ToolNode) for node in nodes)
    assert any(isinstance(edge, ModelGenerateEdge) for edge in edges)
    assert any(isinstance(edge, ToolCallEdge) for edge in edges)

@pytest.mark.asyncio
async def test_process_http_response(http_processor, sample_message_response):
    response_data = {
        "status_code": 200,
        "headers": {},
        "body": sample_message_response.model_dump_json()
    }
    
    result = await http_processor.process(
        HookEventType.HTTP_RESPONSE, 
        response_data
    )
    
    assert result is not None
    nodes, edges = result
    assert len(nodes) == 0  # Response doesn't create new nodes
    assert any(isinstance(edge, ModelGenerateEdge) for edge in edges)
    assert any(isinstance(edge, ToolCallEdge) for edge in edges)

@pytest.mark.asyncio
async def test_handle_invalid_payload(http_processor):
    invalid_data = {
        "method": "POST",
        "url": "http://test.com",
        "headers": {},
        "body": '{"invalid": "json"}'
    }
    
    result = await http_processor.process(
        HookEventType.HTTP_REQUEST, 
        invalid_data
    )
    
    assert result is None

@pytest.mark.asyncio
async def test_handle_empty_payload(http_processor):
    empty_data = {
        "method": "POST",
        "url": "http://test.com",
        "headers": {},
        "body": None
    }
    
    result = await http_processor.process(
        HookEventType.HTTP_REQUEST, 
        empty_data
    )
    
    assert result is None

def test_parse_nodes_and_edges_message_request(http_processor, sample_message_request):
    result = http_processor._parse_nodes_and_edges(sample_message_request)
    
    assert result is not None
    nodes, edges = result
    
    # Verify nodes
    assert any(isinstance(node, LLMNode) and node.node_id == "gpt-4" for node in nodes)
    assert any(isinstance(node, ToolNode) and node.node_id == "calculator" for node in nodes)
    
    # Verify edges
    assert any(
        isinstance(edge, ModelGenerateEdge) and 
        edge.source_node_id == APP_NODE_ID and 
        edge.target_node_id == "gpt-4" and 
        edge.prompt == "Hello"
        for edge in edges
    )

def test_parse_nodes_and_edges_message_response(http_processor, sample_message_response):
    result = http_processor._parse_nodes_and_edges(sample_message_response)
    
    assert result is not None
    nodes, edges = result
    
    assert len(nodes) == 0  # Response doesn't create new nodes
    assert len(edges) == 2  # One ModelGenerateEdge and one ToolCallEdge
    
    assert any(
        isinstance(edge, ModelGenerateEdge) and 
        edge.source_node_id == "gpt-4" and 
        edge.target_node_id == APP_NODE_ID and 
        edge.prompt == "Hello there"
        for edge in edges
    )