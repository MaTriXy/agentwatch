import logging
from typing import Any, Optional

from pydantic import ValidationError

from spyllm.enums import HookEventType
from spyllm.graph.models import GraphExtractor
from spyllm.hooks.http.models import HTTPRequestData, HTTPResponseData
from spyllm.llm.anthropic_models import AnthropicRequestModel, AnthropicResponseModel
from spyllm.llm.ollama_models import OllamaRequestModel, OllamaResponseModel
from spyllm.llm.openai_models import OpenAIRequestModel, OpenAIResponseModel
from spyllm.processing.base import BaseProcessor, GraphStructure
from spyllm.processing.normalizer.base import BaseHTTPContentNormalizer
from spyllm.processing.normalizer.ndjson_normalizer import NdjsonContentNormalizer

logger = logging.getLogger(__name__)

class HttpProcessor(BaseProcessor):
    def __init__(self) -> None:
        super().__init__()
        self._supported_events = [
            HookEventType.HTTP_REQUEST,
            HookEventType.HTTP_RESPONSE
        ]

        self._content_normalizers: list[BaseHTTPContentNormalizer] = [
            NdjsonContentNormalizer()
        ]

    async def process(self, event_type: HookEventType, data: dict[str, Any]) -> Optional[GraphStructure]:
        model_mapping: dict[HookEventType, type[HTTPRequestData | HTTPResponseData]] = {
            HookEventType.HTTP_REQUEST: HTTPRequestData,
            HookEventType.HTTP_RESPONSE: HTTPResponseData
        }

        payload: HTTPRequestData | HTTPResponseData = model_mapping[event_type].model_validate(data)
        return await self._handle_payload(payload)

    async def _handle_payload(self, reqres: HTTPRequestData | HTTPResponseData) -> Optional[GraphStructure]:
        # TODO: Replace this brute force approach with something more targeted, i.e per-provider processor
        request_models: list[type[GraphExtractor]] = [AnthropicRequestModel, AnthropicResponseModel, 
                                                      OllamaRequestModel, OllamaResponseModel,
                                                      OpenAIRequestModel, OpenAIResponseModel]

        body: Optional[str] = reqres.body

        if body is not None:
            for normalizer in self._content_normalizers:
                if reqres.headers.get("content-type") in normalizer.supported_content_types:
                    body = normalizer.normalize(body)
                    break

            for req_model_type in request_models:
                try:
                    req_model = req_model_type.model_validate_json(body)
                    return self._parse_nodes_and_edges(req_model)
                except ValidationError as e:
                    continue

        logger.warning(f"Did not find a suitable model for: {body}")

        return None
    
    def _parse_nodes_and_edges(self, payload: GraphExtractor, **kwargs: Any) -> Optional[GraphStructure]:
       nodes, edges = payload.extract_graph_structure()
       logger.debug(f"Extracted nodes: {nodes}, edges: {edges}")
       return nodes, edges
