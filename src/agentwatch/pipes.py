import asyncio
import logging
import time
from multiprocessing.connection import Connection
from typing import Optional

from pydantic import BaseModel, ValidationError

from agentwatch.models import CommandResponse

logger = logging.getLogger(__name__)

class Pipes:
    """Manages pipes for IPC"""
    def __init__(self) -> None:
        pass

    @classmethod
    async def read_payload(cls, reader_fd: Connection) -> Optional[str]:
        """
        Read a payload from pipe asynchronously.
        This is used by the library process.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, reader_fd.recv)

    @classmethod
    def write_payload_sync(cls, writer_fd: Connection, payload: BaseModel) -> None:
        """
        Write a command to the command pipe synchronously.
        This is used by the client process.
        """
        try:
            writer_fd.send(payload.model_dump_json())
        except Exception as e:
            logger.error(f"Error writing payload: {e}")

    @classmethod
    async def write_payload(cls, writer_fd: Connection, payload: BaseModel) -> None:
        """
        Write a command to the command pipe synchronously.
        This is used by the client process.
        """
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, writer_fd.send, payload.model_dump_json())
        except Exception as e:
            logger.error(f"Error writing payload: {e}")

    @classmethod
    def read_response(cls, reader_fd: Connection, timeout: float = 5.0) -> Optional[CommandResponse]:
        """
        Read a response from the response pipe synchronously with timeout.
        This is used by the client process.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                data = reader_fd.recv()
                return CommandResponse.model_validate_json(data)
            except BlockingIOError:
                # No data available yet
                time.sleep(0.01)
                continue
            except ValidationError as e:
                logger.error(f"Error decoding response: {e}")
                return None
            
        # Timeout reached
        raise TimeoutError(f"Timeout waiting for response")

