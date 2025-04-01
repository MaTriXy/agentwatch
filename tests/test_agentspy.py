import multiprocessing
from unittest.mock import MagicMock, patch

import pytest

from agentspy.client import AgentspyClient
from agentspy.enums import CommandAction
from agentspy.models import Command, CommandResponse


@pytest.fixture
def mock_setup():
    """Fixture that mocks the dependencies and returns them for use in tests"""
    with patch('multiprocessing.Process') as mock_process, \
         patch('multiprocessing.Pipe', return_value=(MagicMock(), MagicMock())) as mock_pipe, \
         patch('multiprocessing.Event') as mock_event, \
         patch('atexit.register') as mock_atexit:
        
        # Create mocks we need to access in tests
        mock_client_fd = mock_pipe.return_value[0]
        mock_agentspy_fd = mock_pipe.return_value[1]
        
        # Create a real event for testing
        exit_event = multiprocessing.Event()
        mock_event.return_value = exit_event
        
        yield {
            'mock_process': mock_process,
            'mock_pipe': mock_pipe,
            'mock_event': mock_event,
            'mock_atexit': mock_atexit,
            'mock_client_fd': mock_client_fd,
            'mock_agentspy_fd': mock_agentspy_fd,
            'exit_event': exit_event
        }


@pytest.fixture
def client(mock_setup):
    """Fixture that creates a AgentspyClient with mocked dependencies"""
    return AgentspyClient()


def test_init(client, mock_setup):
    """Test that initialization creates appropriate objects and starts process"""
    mock_setup['mock_atexit'].assert_called_once_with(client._cleanup)
    mock_setup['mock_process'].assert_called_once()
    mock_setup['mock_process'].return_value.start.assert_called_once()
    assert client._running is True


def test_send_command(client):
    """Test that send_command creates and sends a command"""
    with patch('agentspy.pipes.Pipes.write_payload_sync') as mock_write:
        callback_id = client.send_command(CommandAction.EVENT, {"param1": "value1"})
        
        # Verify command was written with correct parameters
        mock_write.assert_called_once()
        cmd = mock_write.call_args[0][1]
        assert cmd.action == CommandAction.EVENT
        assert cmd.params == {"param1": "value1"}
        assert cmd.callback_id == callback_id


def test_send_command_not_running(client):
    """Test that send_command raises an error when client is not running"""
    client._running = False
    with pytest.raises(RuntimeError):
        client.send_command(CommandAction.EVENT)


def test_send_command_wait(client):
    """Test that send_command_wait sends command and waits for response"""
    with patch('agentspy.pipes.Pipes.write_payload_sync') as mock_write, \
         patch('agentspy.pipes.Pipes.read_response') as mock_read, \
         patch('agentspy.models.Command.from_dict') as mock_command:
        
        # Setup mock response
        mock_response = CommandResponse(callback_id="test-id", data={"result": "test"}, success=True)
        mock_read.return_value = mock_response
        
        # Make command ID match response ID
        mock_command.return_value = Command(
            execution_id="test-execution-id",
            action=CommandAction.EVENT,
            params={"param1": "value1"},
            callback_id="test-id"
        )
        
        response = client.send_command_wait(CommandAction.EVENT, {"param1": "value1"})
        
        # Verify command was written
        mock_write.assert_called_once()
        
        # Verify response was read and returned
        mock_read.assert_called_once()
        assert response == mock_response


def test_send_command_wait_timeout(client):
    """Test that send_command_wait raises timeout error when no response"""
    with patch('agentspy.pipes.Pipes.write_payload_sync'), \
         patch('agentspy.pipes.Pipes.read_response') as mock_read:
        
        # Setup mock to raise TimeoutError
        mock_read.side_effect = TimeoutError("Timeout")
        
        with pytest.raises(TimeoutError):
            client.send_command_wait(CommandAction.EVENT, {"param1": "value1"})


def test_send_command_wait_skip_other_responses(client):
    """Test that send_command_wait skips responses with mismatched callback IDs"""
    with patch('agentspy.pipes.Pipes.write_payload_sync'), \
         patch('agentspy.pipes.Pipes.read_response') as mock_read, \
         patch('agentspy.models.Command.from_dict') as mock_command:
        
        # Setup responses with different callback IDs, then the matching one
        response1 = CommandResponse(callback_id="other-id", success=True, data={})
        response2 = CommandResponse(callback_id="test-id", success=True, data={"result": "test"})
        mock_read.side_effect = [response1, response2]
        
        # Make command ID match second response ID
        mock_command.return_value = Command(
            execution_id="test-execution-id",
            action=CommandAction.EVENT,
            params={"param1": "value1"},
            callback_id="test-id"
        )
        
        response = client.send_command_wait(CommandAction.EVENT, {"param1": "value1"})
        
        # Verify correct response was returned
        assert response == response2
        assert mock_read.call_count == 2

def test_shutdown():
    agentspy = AgentspyClient()
    event_processor = agentspy._process

    assert event_processor.is_alive()
    agentspy.shutdown()
    assert not event_processor.is_alive()
    

def test_shutdown_force_kill(client):
    """Test shutdown with force kill"""
    with patch('agentspy.pipes.Pipes.write_payload_sync'), \
         patch('time.sleep'), \
         patch('os.kill') as mock_kill:
        
        # Setup process mock that stays alive after terminate
        process_mock = MagicMock()
        process_mock.is_alive.return_value = True  # Always alive
        process_mock.pid = 12345
        client._process = process_mock
        
        # Shutdown client
        client.shutdown()
        
        # Verify terminate and kill were called
        process_mock.terminate.assert_called_once()
        mock_kill.assert_called_once()
        assert client._running is False


def test_cleanup(client):
    """Test cleanup method"""
    # Setup process mock
    process_mock = MagicMock()
    client._process = process_mock
    
    # Call cleanup
    client._cleanup()
    
    # Verify process terminated
    process_mock.terminate.assert_called_once()


def test_cleanup_not_running(client):
    """Test cleanup when not running"""
    client._running = False
    process_mock = MagicMock()
    client._process = process_mock
    
    # Call cleanup
    client._cleanup()
    
    # Verify process not terminated
    process_mock.terminate.assert_not_called()