from enum import Enum


class NodeType(str, Enum):
    LLM = "llm"
    TOOL = "tool"
    APPLICATION = "app"

class EdgeType(str, Enum):
    MODEL_GENERATE = "model_generate"
    TOOL_CALL = "tool_call"