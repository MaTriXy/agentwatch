import asyncio
import logging
from typing import Optional

import aiohttp

from spyllm.graph.graph import GraphStructure
from spyllm.protos import WebhookHandlerProto
from spyllm.webhooks.enums import WebhookEventType
from spyllm.webhooks.models import Webhook, WebhookEvent

logger = logging.getLogger(__name__)

class WebhookHandler(WebhookHandlerProto):
    def __init__(self) -> None:
        self._webhooks: dict[str, Webhook] = {}

        self._session = aiohttp.ClientSession()

    async def close(self) -> None:
        await self._session.close()

    async def _send_webhook(self, webhook: Webhook, event: WebhookEvent) -> None:
        try:
            async with self._session.request(webhook.method, 
                                             webhook.url, 
                                             headers=webhook.headers, 
                                             json=event.model_dump()) as response:
                logger.debug(f"Webhook response: {response.status}")
        except aiohttp.ClientError as e:
            logger.error(f"Error sending webhook: {e}")
        finally:
            await aiohttp.ClientSession().close()

    async def notify_webhooks(self, structure: GraphStructure) -> None:
        nodes_event: Optional[WebhookEvent] = None
        edges_event: Optional[WebhookEvent] = None

        if (nodes := structure[0]) is not None:
            nodes_event = WebhookEvent(event_type=WebhookEventType.NODES, data=[n.model_dump() for n in nodes])
        if (edges := structure[1]) is not None:
            edges_event = WebhookEvent(event_type=WebhookEventType.EDGES, data=[e.model_dump() for e in edges])
        
        tasks: list[asyncio.Task[None]] = []

        # First notify about nodes, then edges. For the POC this is good enough (TODO: sort them by create_at)
        if nodes_event:
            for webhook in self.get_webhooks():
                tasks.append(asyncio.create_task(self._send_webhook(webhook, nodes_event)))

            await asyncio.gather(*tasks)

        tasks.clear()
        if edges_event:
            for webhook in self.get_webhooks():
                tasks.append(asyncio.create_task(self._send_webhook(webhook, edges_event)))

            await asyncio.gather(*tasks)


    def register_webhook(self, webhook: Webhook) -> None:
        logger.debug(f"Registering webhook: {webhook.method} {webhook.url}")
        self._webhooks[webhook.guid] = webhook

    def get_webhooks(self) -> list[Webhook]:
        return list(self._webhooks.values())

    def remove_webhook(self, guid: str) -> None:
        if webhook := self._webhooks.get(guid):
            logger.debug(f"Removing webhook: {webhook}")
            del self._webhooks[guid]

    
