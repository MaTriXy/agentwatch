import atexit
import logging
import multiprocessing
import multiprocessing.synchronize
import os
import signal
import time
import uuid
from typing import Any, Optional, Type

from spyllm.enums import CommandAction
from spyllm.event_processing import SpyLLM
from spyllm.hooks.base import BaseHook, HookCallbackProto
from spyllm.hooks.http.http_base_hook import HttpInterceptHook
from spyllm.hooks.http.httpcore_hook import HttpcoreHook
from spyllm.hooks.models import HookEvent
from spyllm.models import Command, CommandResponse
from spyllm.pipes import Pipes

logger = logging.getLogger(__name__)
class SpyLLMClient(HookCallbackProto):
    def __init__(self) -> None:
        self._process: Optional[multiprocessing.Process] = None
        self._running = False

        self._exit_ready_event = multiprocessing.Event()
        self._initialized_event = multiprocessing.Event()

        self._client_fd, self._spyllm_fd = multiprocessing.Pipe()
        self._spyllm = SpyLLM()

        self._llm_hosts =[
            "api.openai.com",
            "api.anthropic.com",
            "api.cohere.ai",
            "api.mistral.ai",
            "api.groq.com",
            "api.together.xyz",
            "localhost",
            "127.0.0.1"
        ]

        self._apply_hooks([
            HttpcoreHook
        ])

        atexit.register(self._cleanup)

        self._execution_id = uuid.uuid4().hex
        self._start_spyllm()

    def set_verbose(self) -> None:
        logger.setLevel(logging.DEBUG)
        
    async def on_hook_callback(self, hook: BaseHook, obj: HookEvent) -> None:
        logger.debug(f"Hook callback received: {obj.event_type}")
        self.send_command(CommandAction.EVENT, obj.model_dump())
        
    def on_hook_callback_sync(self, hook: BaseHook, obj: HookEvent) -> None:
        logger.debug(f"Hook callback received: {obj.event_type}")
        self.send_command(CommandAction.EVENT, obj.model_dump())

    def send_command(self, action: CommandAction, params: Optional[dict[str, Any]] = None) -> str:
        """
        Send a command to the library process without waiting for response
        
        Args:
            action: Command action name
            params: Optional parameters for the command
            
        Returns:
            Callback ID that can be used to correlate the response
        """
        if not self._running:
            raise RuntimeError("Library is not initialized")
        
        cmd = Command.from_dict(self._execution_id, action, params)
        self._write_command(cmd)
        
        return cmd.callback_id
    
    def send_command_wait(self, action: CommandAction, params: Optional[dict[str, Any]] = None, timeout: float = 5.0) -> Optional[CommandResponse]:
        """
        Send a command and wait for the response
        
        Args:
            action: Command action name
            params: Optional parameters for the command
            timeout: Maximum time to wait for response in seconds
            
        Returns:
            Response object
        """
        if not self._running:
            raise RuntimeError("Library is not initialized")
        
        # Create and send command
        cmd = Command.from_dict(self._execution_id, action, params)
        self._write_command(cmd)
        
        # Wait for response with timeout
        while True:
            try:
                response = self._read_response(timeout)
                if response:
                    if response.callback_id == cmd.callback_id:
                        logger.debug(f"Received response: {response}")
                        return response
                    else:
                        logger.debug(f"Skipping response with id {response.callback_id}")
                        continue
                else:
                    # TODO: Fix timeout stuff
                    logger.debug("No response received")
                    return None
            except TimeoutError:
                raise TimeoutError(f"Timeout waiting for response to {action}")

    def _start_spyllm(self) -> None:
        """Initialize the library by starting the process"""
        if self._running:
            logger.warning("Library is already initialized")
            return
        
        logger.debug("Initializing library process")
        self._process = multiprocessing.Process(
            target=self._spyllm.start,
            args=(self._client_fd, self._initialized_event, self._exit_ready_event),
            daemon=True
        )
        
        self._process.start()
        self._running = True
        
        self._initialized_event.wait(1)

        logger.debug(f"Library process started with PID {self._process.pid}")
        
    
    def _apply_hooks(self, hooks: list[Type[BaseHook]]) -> None:
        for hook in hooks:
            hook_instance = hook(callback_handler=self)
            hook_instance.apply_hook()
            
            if isinstance(hook_instance, HttpInterceptHook):
                for host in self._llm_hosts:
                    hook_instance.add_intercept_rule(host)
                    
    def _cleanup(self) -> None:
        """Cleanup function called on program exit"""
        if self._running:
            self.shutdown()

    def _write_command(self, command: Command) -> None:
        """Write a command to the command pipe"""
        try:
            logger.debug(f"Sending command: {command.action}:{command.callback_id} to fd {self._spyllm_fd.fileno()}")
            Pipes.write_payload_sync(self._spyllm_fd, command)
        except Exception as e:
            logger.error(f"Error writing command: {e}")
            raise
    
    def _read_response(self, timeout: float = 5.0) -> Optional[CommandResponse]:
        """Read a response from the response pipe with timeout"""
        return Pipes.read_response(self._spyllm_fd, timeout)

    def shutdown(self) -> None:
        """Shut down the library process"""
        if not self._running:
            logger.warning("Library is not running")
            return
        
        logger.debug("Shutting down spyllm")
        try:
            # Send shutdown command
            self.send_command(CommandAction.SHUTDOWN)
            
            # Give the process some time to terminate gracefully and wait for exit event
            self._exit_ready_event.wait(5)
            start_time = time.time()
            while self._process and self._process.is_alive() and time.time() - start_time < 1:
                time.sleep(0.1)

            # Force terminate if still running
            if self._process and self._process.is_alive():
                logger.warning("SpyLLM didn't shut down gracefully, terminating")
                self._process.terminate()
                
                # Wait for process to terminate
                time.sleep(0.5)
                
                # If still alive, kill it
                if self._process.is_alive() and self._process.pid:
                    logger.warning("Process didn't terminate, killing")
                    os.kill(self._process.pid, signal.SIGKILL)
        except Exception as e:
            logger.error(f"Error shutting down process: {e}")
        finally:
            self._running = False
            logger.debug("Library shutdown complete")      