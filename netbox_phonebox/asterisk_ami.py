import socket
import re
import time
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger('netbox_phonebox.ami')


class AsteriskAMI:
    """Asterisk Manager Interface client"""
    
    def __init__(self, host: str, port: int, username: str, secret: str):
        self.host = host
        self.port = port
        self.username = username
        self.secret = secret
        self.socket = None
        self.connected = False
        logger.info(f"Initializing AMI client for {host}:{port}")
    
    def connect(self) -> bool:
        """Connect to AMI"""
        try:
            logger.info(f"Connecting to AMI at {self.host}:{self.port}")
            
            # Создаем сокет
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            
            # TCP подключение
            logger.info(f"Attempting TCP connection to {self.host}:{self.port}")
            try:
                self.socket.connect((self.host, self.port))
                logger.info(f"TCP connection established")
            except (socket.timeout, ConnectionRefusedError, OSError) as e:
                logger.error(f"TCP connection failed: {e}")
                self._cleanup_socket()
                return False
            
            # Read welcome message
            logger.info("Reading welcome message...")
            try:
                self.socket.settimeout(5)
                welcome_data = self.socket.recv(1024)
                welcome = welcome_data.decode('utf-8', errors='ignore')
                logger.info(f"Welcome: {welcome.strip()}")
            except socket.timeout:
                logger.error("Timeout reading welcome message")
                self._cleanup_socket()
                return False
            
            if 'Asterisk Call Manager' not in welcome:
                logger.error(f"Invalid welcome message: {welcome}")
                self._cleanup_socket()
                return False
            
            # Send login
            logger.info(f"Sending login for user: {self.username}")
            login_msg = f"Action: Login\r\nUsername: {self.username}\r\nSecret: {self.secret}\r\n\r\n"
            
            try:
                self.socket.sendall(login_msg.encode('utf-8'))
                logger.info("Login sent")
            except Exception as e:
                logger.error(f"Error sending login: {e}")
                self._cleanup_socket()
                return False
            
            # Read login response (может содержать несколько блоков)
            logger.info("Reading login response...")
            try:
                self.socket.settimeout(5)
                response = self._read_login_response()
                logger.info(f"Login response received ({len(response)} bytes)")
                logger.debug(f"Response: {response}")
            except socket.timeout:
                logger.error("Timeout reading login response")
                self._cleanup_socket()
                return False
            except Exception as e:
                logger.error(f"Error reading login response: {e}")
                self._cleanup_socket()
                return False
            
            # Check for success
            response_lower = response.lower()
            
            if 'response: success' in response_lower:
                self.connected = True
                logger.info("✓ Successfully authenticated to AMI")
                return True
            elif 'authentication failed' in response_lower:
                logger.error("✗ Authentication failed - check username/password")
                self._cleanup_socket()
                return False
            elif 'permission denied' in response_lower:
                logger.error("✗ Permission denied - check user permissions")
                self._cleanup_socket()
                return False
            else:
                logger.error(f"✗ Unexpected response: {response[:200]}")
                self._cleanup_socket()
                return False
            
        except Exception as e:
            logger.error(f"AMI Connection Error: {e}", exc_info=True)
            self._cleanup_socket()
            return False
    
    def _read_login_response(self) -> str:
        """
        Read login response from AMI
        
        Grandstream UCM sends multiple blocks:
        1. Response: Success
        2. Event: SuccessfulAuth
        
        We need to read until we find 'Response: Success'
        """
        response = ""
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            try:
                # Read a chunk
                data = self.socket.recv(4096)
                if not data:
                    logger.warning("No more data")
                    break
                
                chunk = data.decode('utf-8', errors='ignore')
                response += chunk
                logger.debug(f"Iteration {iteration}: received {len(data)} bytes")
                
                # Check if we have Response: Success
                if 'Response: Success' in response:
                    logger.debug("Found 'Response: Success'")
                    # Wait a bit for any additional data (like Event: SuccessfulAuth)
                    time.sleep(0.1)
                    
                    # Try to read any remaining data (non-blocking)
                    self.socket.settimeout(0.1)
                    try:
                        extra_data = self.socket.recv(4096)
                        if extra_data:
                            extra_chunk = extra_data.decode('utf-8', errors='ignore')
                            response += extra_chunk
                            logger.debug(f"Received additional {len(extra_data)} bytes")
                    except socket.timeout:
                        pass  # No more data, that's OK
                    
                    # Restore timeout
                    self.socket.settimeout(5)
                    break
                
                # If response is getting too large, stop
                if len(response) > 10000:
                    logger.warning("Response too large, stopping")
                    break
                    
            except socket.timeout:
                logger.debug("Timeout waiting for more data")
                break
        
        return response
    
    def _cleanup_socket(self):
        """Close and cleanup socket"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        self.connected = False
    
    def disconnect(self):
        """Disconnect from AMI"""
        if self.socket:
            try:
                logger.info("Disconnecting from AMI")
                if self.connected:
                    try:
                        self._send_action('Logoff')
                        # Wait a bit for response
                        time.sleep(0.1)
                    except:
                        pass
                self.socket.close()
            except Exception as e:
                logger.warning(f"Error during disconnect: {e}")
            finally:
                self.connected = False
                self.socket = None
                logger.info("Disconnected from AMI")
    
    def _send_action(self, action: str, params: Optional[Dict[str, str]] = None):
        """Send AMI action"""
        if not self.socket:
            raise Exception("Not connected to AMI")
        
        message = f"Action: {action}\r\n"
        
        if params:
            for key, value in params.items():
                message += f"{key}: {value}\r\n"
        
        message += "\r\n"
        
        logger.debug(f"Sending AMI action: {action}")
        self.socket.sendall(message.encode('utf-8'))
    
    def _read_response(self, timeout: Optional[int] = None) -> str:
        """Read AMI response"""
        if timeout:
            old_timeout = self.socket.gettimeout()
            self.socket.settimeout(timeout)
        
        try:
            response = ""
            max_iterations = 20
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                
                try:
                    data = self.socket.recv(4096)
                    if not data:
                        break
                    
                    chunk = data.decode('utf-8', errors='ignore')
                    response += chunk
                    
                    # Check if we have a complete response
                    # Look for Response: or Event: followed by double newline
                    if '\r\n\r\n' in response:
                        # Check if this looks like a complete message
                        lines = response.split('\r\n')
                        if any(line.startswith('Response:') or line.startswith('Event:') for line in lines):
                            break
                    
                    # Safety check
                    if len(response) > 50000:
                        logger.warning("Response too large")
                        break
                        
                except socket.timeout:
                    if response:
                        break  # We have some data, that's enough
                    raise
            
            logger.debug(f"Received AMI response: {len(response)} bytes")
            return response
            
        finally:
            if timeout:
                self.socket.settimeout(old_timeout)
    
    def __enter__(self):
        """Context manager entry"""
        if not self.connect():
            raise Exception("Failed to connect to AMI")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
        return False
    
    def originate_call(self, channel: str, extension: str, caller_id: str, 
                       context: str = 'from-internal', priority: int = 1) -> Dict[str, Any]:
        """
        Originate a call
        
        Args:
            channel: Channel to call (e.g., 'PJSIP/100')
            extension: Extension to dial
            caller_id: Caller ID to use
            context: Dialplan context
            priority: Dialplan priority
        
        Returns:
            Dict with success status and message
        """
        try:
            if not self.connected:
                return {
                    'success': False,
                    'message': 'Not connected to PBX'
                }
            
            logger.info(f"Originating call: {channel} -> {extension}")
            
            self._send_action('Originate', {
                'Channel': channel,
                'Exten': extension,
                'Context': context,
                'Priority': str(priority),
                'CallerID': caller_id,
                'Async': 'true'
            })
            
            response = self._read_response(timeout=5)
            logger.info(f"Originate response: {response[:200]}")
            
            if 'Response: Success' in response or 'success' in response.lower():
                return {
                    'success': True,
                    'message': 'Call initiated successfully'
                }
            else:
                return {
                    'success': False,
                    'message': f'Failed to initiate call: {response[:200]}'
                }
                
        except Exception as e:
            logger.error(f"Error originating call: {e}", exc_info=True)
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
    
    def get_channel_status(self, channel: str = '') -> Dict[str, Any]:
        """
        Get channel status
        
        Args:
            channel: Channel name (empty for all channels)
        
        Returns:
            Dict with channel status
        """
        try:
            if not self.connected:
                return {
                    'success': False,
                    'message': 'Not connected to PBX'
                }
            
            params = {}
            if channel:
                params['Channel'] = channel
            
            self._send_action('Status', params)
            
            response = self._read_response(timeout=5)
            
            if 'Response: Success' in response or 'success' in response.lower():
                return {
                    'success': True,
                    'response': response
                }
            else:
                return {
                    'success': False,
                    'message': 'Channel not found',
                    'response': response
                }
                
        except Exception as e:
            logger.error(f"Error getting channel status: {e}", exc_info=True)
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
    
    def hangup(self, channel: str) -> Dict[str, Any]:
        """
        Hangup a channel
        
        Args:
            channel: Channel to hangup
        
        Returns:
            Dict with success status
        """
        try:
            if not self.connected:
                return {
                    'success': False,
                    'message': 'Not connected to PBX'
                }
            
            logger.info(f"Hanging up channel: {channel}")
            
            self._send_action('Hangup', {
                'Channel': channel
            })
            
            response = self._read_response(timeout=5)
            
            if 'Response: Success' in response or 'success' in response.lower():
                return {
                    'success': True,
                    'message': 'Channel hung up'
                }
            else:
                return {
                    'success': False,
                    'message': f'Failed to hangup: {response[:200]}'
                }
                
        except Exception as e:
            logger.error(f"Error hanging up: {e}", exc_info=True)
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }