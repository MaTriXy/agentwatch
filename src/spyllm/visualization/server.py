
import logging
import os
from pathlib import Path
from typing import Any, Type

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from spyllm.graph.enums import EdgeType, NodeType
from spyllm.graph.models import Edge, LLMNode, ModelGenerateEdge, Node, ToolCallEdge, ToolNode
from spyllm.visualization.consts import API_EDGES, API_EVENTS, API_NODES
from spyllm.visualization.enums import WebsocketEvent
from spyllm.visualization.models import WebsocketMessage
from spyllm.webhooks.enums import WebhookEventType
from spyllm.webhooks.models import WebhookEvent

logger = logging.getLogger(__name__)

app = FastAPI()
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend/dist")
app.mount("/ui", StaticFiles(directory=static_dir, html=True), name="static")
app.mount("/assets", StaticFiles(directory=Path(static_dir) / "assets", html=True), name="static")

connections: list[WebSocket] = []
app_nodes: list[Node] = []
app_edges: list[Edge] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint"""
    await websocket.accept()
    connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connections.remove(websocket)

def create_edge_from_data(edge_data: dict[str, Any]) -> Edge:
    edge_type = EdgeType(edge_data.get("edge_type"))
    
    edge_class_map: dict[EdgeType, Type[Edge]] = {
        EdgeType.TOOL_CALL: ToolCallEdge,
        EdgeType.MODEL_GENERATE: ModelGenerateEdge
    }
    
    edge_class = edge_class_map.get(edge_type, Edge)
    return edge_class.model_validate(edge_data)

@app.post(API_EDGES)
async def add_edges(edges: list[Edge]) -> dict[str, Any]:
    """Add edges to the graph"""
    app_edges.extend(edges)

    message = WebsocketMessage(type=WebsocketEvent.ADD_EDGE, data=[e.model_dump() for e in app_edges])
    for conn in connections:
        await conn.send_json(message.model_dump())
    
    return {"message": "edges added", "node": edges}

def create_node_from_data(node_data: dict[str, Any]) -> Node:
    """Factory function to create the appropriate Node subclass instance."""
    node_type = NodeType(node_data.get("node_type"))
    
    node_class_map: dict[NodeType, Type[Node]] = {
        NodeType.LLM: LLMNode,
        NodeType.TOOL: ToolNode,
    }
    
    node_class = node_class_map.get(node_type, Node)
    return node_class.model_validate(node_data)

@app.post(API_NODES)
async def add_nodes(nodes: list[Node]) -> dict[str, Any]:
    """Add nodes to the graph"""
    new_nodes: list[Node] = []
    for n in nodes:
        if n.node_id not in [n.node_id for n in app_nodes]:
            new_nodes.append(n)

    app_nodes.extend(new_nodes)

    if new_nodes:
        message = WebsocketMessage(type=WebsocketEvent.ADD_NODE, data=[n.model_dump() for n in app_nodes])
        for conn in connections:
            await conn.send_json(message.model_dump())

    return {"message": "Node added", "node": nodes}

@app.post(API_EVENTS)
async def handle_events(event: WebhookEvent) -> dict[str, Any]:
    """Handle events"""
    print(f"{event.model_dump()}")

    match event.event_type:
        case WebhookEventType.NODES:
            await add_nodes([create_node_from_data(n) for n in event.data])
        case WebhookEventType.EDGES:
            await add_edges([create_edge_from_data(e) for e in event.data])
        case _:
            pass

    return {"message": "Event sent", "event": event}