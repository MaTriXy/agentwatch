from enum import Enum


class NodeType(str, Enum):
    LLM = "llm"
    TOOL = "tool"
    APPLICATION = "app"

class EdgeType(str, Enum):
    MODEL_GENERATE = "model_generate"
    TOOL_CALL = "tool_call"

class HttpModel(str, Enum):
    OLLAMA_REQUEST = "ollama_request"
    OLLAMA_RESPONSE = "ollama_response"
    ANTHROPIC_REQUEST = "anthropic_request"
    ANTHROPIC_RESPONSE = "anthropic_response"
    OPENAI_REQUEST = "openai_request"
    OPENAI_RESPONSE = "openai_response"
    OLLAMA_GENERATE_REQUEST = "ollama_generate_request"
    OLLAMA_GENERATE_RESPONSE = "ollama_generate_response"
    