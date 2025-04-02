import multiprocessing
import time
import unittest
from unittest.mock import ANY, MagicMock, patch

from agentwatch.client import AgentwatchClient
from agentwatch.enums import CommandAction
from agentwatch.models import Command, CommandResponse


class TestAgentwatchClient(unittest.TestCase):
    
    @patch('multiprocessing.Process')
    @patch('multiprocessing.Pipe', return_value=(MagicMock(), MagicMock()))
    @patch('multiprocessing.Event')
    @patch('atexit.register')
    def setUp(self, mock_atexit, mock_event, mock_pipe, mock_process):
        self.mock_process = mock_process
        self.mock_pipe = mock_pipe
        self.mock_event = mock_event
        self.mock_atexit = mock_atexit
        
        self.mock_client_fd = mock_pipe.return_value[0]
        self.mock_agentwatch_fd = mock_pipe.return_value[1]
        
        # Create a real event for testing
        self.exit_event = multiprocessing.Event()
        mock_event.return_value = self.exit_event
        
        # Create client instance
        self.client = AgentwatchClient()
        
    def test_init(self):
        """Test that initialization creates appropriate objects and starts process"""
        self.mock_atexit.assert_called_once_with(self.client._cleanup)
        self.mock_process.assert_called_once()
        self.mock_process.return_value.start.assert_called_once()
        self.assertTrue(self.client._running)
        
    @patch('agentwatch.pipes.Pipes.write_payload_sync')
    def test_send_command(self, mock_write):
        """Test that send_command creates and sends a command"""
        callback_id = self.client.send_command(CommandAction.EVENT, {"param1": "value1"})
        
        # Verify command was written with correct parameters
        mock_write.assert_called_once()
        cmd = mock_write.call_args[0][1]
        self.assertEqual(cmd.action, CommandAction.EVENT)
        self.assertEqual(cmd.params, {"param1": "value1"})
        self.assertEqual(cmd.callback_id, callback_id)
        
    def test_send_command_not_running(self):
        """Test that send_command raises an error when client is not running"""
        self.client._running = False
        with self.assertRaises(RuntimeError):
            self.client.send_command(CommandAction.EVENT)
            
    @patch('agentwatch.pipes.Pipes.write_payload_sync')
    @patch('agentwatch.pipes.Pipes.read_response')
    def test_send_command_wait(self, mock_read, mock_write):
        """Test that send_command_wait sends command and waits for response"""
        # Setup mock response
        mock_response = CommandResponse(callback_id="test-id", data={"result": "test"}, success=True)
        mock_read.return_value = mock_response
        
        # Make command ID match response ID
        with patch('agentwatch.models.Command.from_dict', return_value=Command(
            execution_id="test-execution-id",
            action=CommandAction.EVENT,
            params={"param1": "value1"},
            callback_id="test-id"
        )):
            response = self.client.send_command_wait(CommandAction.EVENT, {"param1": "value1"})
        
        # Verify command was written
        mock_write.assert_called_once()
        
        # Verify response was read and returned
        mock_read.assert_called_once()
        self.assertEqual(response, mock_response)
        
    @patch('agentwatch.pipes.Pipes.write_payload_sync')
    @patch('agentwatch.pipes.Pipes.read_response')
    def test_send_command_wait_timeout(self, mock_read, mock_write):
        """Test that send_command_wait raises timeout error when no response"""
        # Setup mock to raise TimeoutError
        mock_read.side_effect = TimeoutError("Timeout")
        
        with self.assertRaises(TimeoutError):
            self.client.send_command_wait(CommandAction.EVENT, {"param1": "value1"})
            
    @patch('agentwatch.pipes.Pipes.write_payload_sync')
    @patch('agentwatch.pipes.Pipes.read_response')
    def test_send_command_wait_skip_other_responses(self, mock_read, mock_write):
        """Test that send_command_wait skips responses with mismatched callback IDs"""
        # Setup responses with different callback IDs, then the matching one
        response1 = CommandResponse(callback_id="other-id", success=True, data={})
        response2 = CommandResponse(callback_id="test-id", success=True, data={"result": "test"})
        mock_read.side_effect = [response1, response2]
        
        # Make command ID match second response ID
        with patch('agentwatch.models.Command.from_dict', return_value=Command(
            execution_id="test-execution-id",
            action=CommandAction.EVENT,
            params={"param1": "value1"},
            callback_id="test-id"
        )):
            response = self.client.send_command_wait(CommandAction.EVENT, {"param1": "value1"})
        
        # Verify correct response was returned
        self.assertEqual(response, response2)
        self.assertEqual(mock_read.call_count, 2)
        
    @patch('agentwatch.pipes.Pipes.write_payload_sync')
    def test_shutdown(self, mock_write):
        """Test normal shutdown process"""
        # Setup process mock
        process_mock = MagicMock()
        process_mock.is_alive.return_value = False
        self.client._process = process_mock
        
        # Simulate normal shutdown
        self.client.shutdown()
        
        # Verify shutdown command sent
        mock_write.assert_called_once()
        cmd = mock_write.call_args[0][1]
        self.assertEqual(cmd.action, CommandAction.SHUTDOWN)
        
        # Verify process state checked
        process_mock.is_alive.assert_called()
        self.assertFalse(self.client._running)
        
    @patch('agentwatch.pipes.Pipes.write_payload_sync')
    @patch('time.sleep')
    @patch('os.kill')
    def test_shutdown_force_kill(self, mock_kill, mock_sleep, mock_write):
        """Test shutdown with force kill"""
        # Setup process mock that stays alive after terminate
        process_mock = MagicMock()
        process_mock.is_alive.return_value = True  # Always alive
        process_mock.pid = 12345
        self.client._process = process_mock
        
        # Shutdown client
        self.client.shutdown()
        
        # Verify terminate and kill were called
        process_mock.terminate.assert_called_once()
        mock_kill.assert_called_once()
        self.assertFalse(self.client._running)
        
    def test_cleanup(self):
        """Test cleanup method"""
        # Setup process mock
        process_mock = MagicMock()
        self.client._process = process_mock
        
        # Call cleanup
        self.client._cleanup()
        
        # Verify process terminated
        process_mock.terminate.assert_called_once()
        
    def test_cleanup_not_running(self):
        """Test cleanup when not running"""
        self.client._running = False
        process_mock = MagicMock()
        self.client._process = process_mock
        
        # Call cleanup
        self.client._cleanup()
        
        # Verify process not terminated
        process_mock.terminate.assert_not_called()

if __name__ == '__main__':
    unittest.main()