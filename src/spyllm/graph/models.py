import time
import uuid
from abc import abstractmethod
from typing import Any, Type, TypeAlias

from pydantic import BaseModel, Field

from spyllm.graph.consts import APP_NODE_ID
from spyllm.graph.enums import EdgeType, NodeType
from spyllm.utils.flavor_manager import FlavorManager


class GraphExtractor(BaseModel):
    @abstractmethod
    def extract_graph_structure(self) -> "GraphStructure":
        ...

class Node(BaseModel):
    node_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    node_type: NodeType
    created_at: float = Field(default_factory=lambda: time.time())

class LLMNode(Node):
    node_type: NodeType = NodeType.LLM

class ToolNode(Node):
    node_type: NodeType = NodeType.TOOL
    tool_description: str
    
class AppNode(Node):
    node_id: str = APP_NODE_ID
    node_type: NodeType = NodeType.APPLICATION

class Edge(BaseModel):
    edge_type: EdgeType
    source_node_id: str
    target_node_id: str
    created_at: float = Field(default_factory=lambda: time.time())

class ModelGenerateEdge(Edge):
    edge_type: EdgeType = EdgeType.MODEL_GENERATE
    prompt: str

class ToolCallEdge(Edge):
    edge_type: EdgeType = EdgeType.TOOL_CALL
    tool_input: dict[str, Any]

GraphStructure: TypeAlias = tuple[list[Node], list[Edge]]

graph_extractor_fm: FlavorManager[str, Type[GraphExtractor]] = FlavorManager()

