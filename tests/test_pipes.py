import multiprocessing
from multiprocessing import Pipe

import pytest
from pydantic import BaseModel

from spyllm.models import CommandResponse
from spyllm.pipes import Pipes


class MockPayload(BaseModel):
    message: str
    value: int

def test_write_payload_sync():
    """Test synchronous payload writing."""
    parent_conn, child_conn = Pipe()
    payload = MockPayload(message="test", value=42)
    
    Pipes.write_payload_sync(parent_conn, payload)
    
    received = child_conn.recv()
    assert received == payload.model_dump_json()

@pytest.mark.asyncio
async def test_write_payload_async():
    """Test asynchronous payload writing."""
    parent_conn, child_conn = Pipe()
    payload = MockPayload(message="async test", value=123)
    
    await Pipes.write_payload(parent_conn, payload)
    
    received = child_conn.recv()
    assert received == payload.model_dump_json()

@pytest.mark.asyncio
async def test_read_payload():
    """Test reading payload asynchronously."""
    parent_conn, child_conn = Pipe()
    
    # Send data from the other end of the pipe
    test_payload = MockPayload(message="read test", value=456)
    child_conn.send(test_payload.model_dump_json())
    
    # Read payload
    result = await Pipes.read_payload(parent_conn)
    assert result == test_payload.model_dump_json()

def test_read_response_success():
    """Test reading response synchronously."""
    parent_conn, child_conn = Pipe()
    
    # Prepare a response
    response = CommandResponse(success=True, data="Operation completed")
    child_conn.send(response.model_dump_json())
    
    # Read response
    result = Pipes.read_response(parent_conn)
    assert result.success is True
    assert result.data == "Operation completed"

def multiprocess_communication_worker(send_conn, receive_conn):
    """Simulated worker process for multiprocessing communication test."""
    # Simulate receiving a payload
    payload = receive_conn.recv()
    
    # Create and send a response
    response = CommandResponse(
        success=True, 
        data=f"Processed payload: {payload}"
    )
    send_conn.send(response.model_dump_json())

def test_multiprocessing_communication():
    """
    Test full multiprocessing communication scenario 
    demonstrating parent-child process interaction.
    """
    # Create bidirectional pipes
    parent_send, child_receive = Pipe()
    child_send, parent_receive = Pipe()
    
    # Prepare payload
    payload = CommandResponse(data="multiprocess test", success=True)
    
    # Create a process
    process = multiprocessing.Process(
        target=multiprocess_communication_worker, 
        args=(child_send, child_receive)
    )
    
    try:
        # Start the process
        process.start()
        
        # Send payload to child process
        Pipes.write_payload_sync(parent_send, payload)
        
        # Read response from child process
        response = Pipes.read_response(parent_receive)
        
        # Assertions
        assert response is not None
        assert response.success is True
        assert response.data == "Processed payload: " + payload.model_dump_json()

    finally:
        # Clean up
        process.terminate()
        process.join()

def test_payload_validation_error():
    """Test handling of invalid payload."""
    parent_conn, child_conn = Pipe()
    
    # Send invalid JSON
    child_conn.send("invalid json")
    
    # Should return None due to validation error
    result = Pipes.read_response(parent_conn)
    assert result is None