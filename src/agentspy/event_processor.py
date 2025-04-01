import asyncio
import logging
from multiprocessing.connection import Connection
from multiprocessing.synchronize import Event
from typing import Optional

from pydantic import ValidationError

from agentspy.enums import CommandAction
from agentspy.graph.graph import GraphBuilder
from agentspy.hooks.models import HookEvent
from agentspy.models import Command, CommandResponse
from agentspy.pipes import Pipes
from agentspy.processing.base import BaseProcessor
from agentspy.processing.http_processing import HttpProcessor
from agentspy.visualization.consts import VISUALIZATION_SERVER_PORT
from agentspy.webhooks.handler import WebhookHandler
from agentspy.webhooks.models import Webhook

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
    
class EventProcessor:
    NUM_WORKERS = 1

    def __init__(self) -> None:
        logger.info("agentspy initializing...")

        self._exit_event: Optional[Event] = None
        self._init_event: Optional[Event] = None
        self._pipe: Optional[Connection] = None
        self._processors: list[BaseProcessor] = []
        self._command_queue: Optional[asyncio.Queue[Command]] = None
        self._workers: list[asyncio.Task[None]] = []
        self._event_poller: Optional[asyncio.Task[None]] = None

        self._graph_builder = GraphBuilder()
        self._webhook_handler: Optional[WebhookHandler] = None
        self._supported_processors: list[type[BaseProcessor]] = [
            HttpProcessor
            ]
        
        logger.debug("agentspy initialized!")
    
    def start(self, pipe: Connection, init_event: Event, exit_event: Event) -> None: 
        self._pipe = pipe
        self._exit_event = exit_event
        self._init_event = init_event

        asyncio.run(self._start())

        logger.debug("agentspy stopped")
        if self._exit_event:
            self._exit_event.set()

    async def _start(self) -> None:
        self._command_queue = asyncio.Queue()
        self._webhook_handler = WebhookHandler()

        await self._register_processors()

        for task_num in range(self.NUM_WORKERS):
            self._workers.append(asyncio.create_task(self._consume_events(), name=f"task-{task_num}"))
        
        self._register_visualization_webhook()

        logger.debug(f"agentspy up and running")
        if self._init_event:
            self._init_event.set()

        self._event_poller = asyncio.create_task(self._poll_events(), name="event-poller")
        await self._event_poller

        logger.debug("Stopped polling for events")

        await asyncio.gather(*self._workers)

    def _register_visualization_webhook(self) -> None:
        if self._webhook_handler is None:
            return
        
        webhook = Webhook(
            url=f"http://localhost:{VISUALIZATION_SERVER_PORT}/api/events",
        )

        self._webhook_handler.register_webhook(webhook)

    async def _register_processors(self) -> None:
        for processor in self._supported_processors:
            self._processors.append(processor())
            logger.debug(f"Processor registered: {processor.__name__}")

    async def _consume_events(self) -> None:
        logger.debug(f"Worker started: {asyncio.current_task().get_name()}, consuming events")  # type: ignore
        if not self._command_queue or not self._pipe:
            raise RuntimeError("agentspy not initialized")
        
        try:
            while True:
                logger.debug("Waiting for command...")
                cmd = await self._command_queue.get()
                logger.debug(f"Consuming command {cmd.callback_id}")
                response = await self._on_command(cmd)
                logger.debug(f"Command {cmd.callback_id} processed!")

                if response:
                    await Pipes.write_payload(self._pipe, response)
                    logger.debug(f"Response sent: {response}")

                self._command_queue.task_done()
                
        except asyncio.CancelledError as e:
            logger.debug(f"Worker {asyncio.current_task().get_name()} cancelled")  # type: ignore
        except Exception as e:
            logger.error(f"Error consuming events: {e}")
            raise

    async def _poll_events(self) -> None:
        if not self._pipe or not self._command_queue:
            raise RuntimeError("agentspy not initialized")
        
        logger.debug(f"Polling for events @ fd {self._pipe.fileno()}")

        try:
            while True:
                try:
                    payload = await Pipes.read_payload(self._pipe)
                    if payload is None:
                        logger.debug("No payload received")
                        continue

                    cmd = Command.model_validate_json(payload)
                    self._command_queue.put_nowait(cmd)
                except ValidationError as e:
                    logger.error(f"Error decoding payload: {e}")
        except asyncio.CancelledError:
            logger.debug("Event poller cancelled")

    async def _on_command(self, cmd: Command) -> Optional[CommandResponse]:
        logger.debug(f"Event received: {cmd.model_dump_json()}")
        try:
            match (cmd.action):
                case CommandAction.EVENT:
                    event = HookEvent.model_validate(cmd.params)
                    return await self._handle_event(cmd.callback_id, event)
                case CommandAction.ADD_WEBHOOK:
                    webhook = Webhook.model_validate(cmd.params)
                    if self._webhook_handler is not None:
                        self._webhook_handler.register_webhook(webhook)
                    return CommandResponse(success=True, callback_id=cmd.callback_id)
                case CommandAction.SHUTDOWN:
                    await self._shutdown()
                    return CommandResponse(success=True, callback_id=cmd.callback_id)
                case CommandAction.PING:
                    return CommandResponse(success=True, callback_id=cmd.callback_id)
                case CommandAction.VERBOSE:
                    self._set_verbose()
                    return CommandResponse(success=True, callback_id=cmd.callback_id)
        except ValidationError as e:
            logger.error(f"Error decoding event: {e}")
        
        return None
    
    async def _handle_event(self, callback_id: str, event: HookEvent) -> Optional[CommandResponse]:
        for processor in self._processors:
            if processor.can_handle(event.event_type):
                structure = await processor.process(event.event_type, event.data)
                if structure:
                    self._graph_builder.append_structure(structure)
                    if self._webhook_handler is not None:
                        await self._webhook_handler.notify_webhooks(self._graph_builder.get_structure())

                # TODO: Should we break here? The answer is a mystery to be revealed...
                break

        return CommandResponse(success=True, callback_id=callback_id)

    async def _shutdown(self) -> None:
        logger.info("Shutting down agentspy")
        if self._webhook_handler:
            await self._webhook_handler.close()
        
        if self._event_poller:
            self._event_poller.cancel()

        # TODO: Do we gather or do we cancel? The answer is a mystery to be revealed...
        for task in self._workers:
            task.cancel()
        
        logger.debug("agentspy shutdown complete")

    def _set_verbose(self) -> None:
        logging.basicConfig(level=logging.DEBUG)
        for logger_name, logger in logging.root.manager.loggerDict.items():
            if isinstance(logger, logging.Logger):  # Ensure it's a logger
                logger.setLevel(logging.DEBUG)
                for handler in logger.handlers:
                    handler.setLevel(logging.DEBUG)
        