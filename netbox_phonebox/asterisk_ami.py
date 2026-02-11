import socket
import re
from typing import Optional, Dict, Any
from django.conf import settings


class AsteriskAMI:
    """Asterisk Manager Interface client"""
    
    def __init__(self, host: str, port: int, username: str, secret: str):
        self.host = host
        self.port = port
        self.username = username
        self.secret = secret
        self.socket = None
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to AMI"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            
            # Read welcome message
            response = self._read_response()
            if 'Asterisk Call Manager' not in response:
                return False
            
            # Login
            self._send_action('Login', {
                'Username': self.username,
                'Secret': self.secret
            })
            
            response = self._read_response()
            if 'Success' in response:
                self.connected = True
                return True
            
            return False
            
        except Exception as e:
            print(f"AMI Connection Error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from AMI"""
        if self.socket:
            try:
                self._send_action('Logoff')
                self.socket.close()
            except:
                pass
            finally:
                self.connected = False
                self.socket = None
    
    def _send_action(self, action: str, params: Optional[Dict[str, str]] = None):
        """Send AMI action"""
        if not self.socket:
            raise Exception("Not connected to AMI")
        
        message = f"Action: {action}\r\n"
        
        if params:
            for key, value in params.items():
                message += f"{key}: {value}\r\n"
        
        message += "\r\n"
        
        self.socket.sendall(message.encode('utf-8'))
    
    def _read_response(self) -> str:
        """Read AMI response"""
        response = ""
        while True:
            data = self.socket.recv(4096).decode('utf-8')
            response += data
            
            if '\r\n\r\n' in response:
                break
        
        return response
    
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
                if not self.connect():
                    return {
                        'success': False,
                        'message': 'Failed to connect to PBX'
                    }
            
            self._send_action('Originate', {
                'Channel': channel,
                'Exten': extension,
                'Context': context,
                'Priority': str(priority),
                'CallerID': caller_id,
                'Async': 'true'
            })
            
            response = self._read_response()
            
            if 'Success' in response:
                return {
                    'success': True,
                    'message': 'Call initiated successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to initiate call'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
    
    def get_channel_status(self, channel: str) -> Dict[str, Any]:
        """Get channel status"""
        try:
            if not self.connected:
                if not self.connect():
                    return {'success': False, 'message': 'Not connected'}
            
            self._send_action('Status', {'Channel': channel})
            response = self._read_response()
            
            return {
                'success': True,
                'response': response
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }
    
    def hangup(self, channel: str) -> Dict[str, Any]:
        """Hangup a channel"""
        try:
            if not self.connected:
                if not self.connect():
                    return {'success': False, 'message': 'Not connected'}
            
            self._send_action('Hangup', {'Channel': channel})
            response = self._read_response()
            
            if 'Success' in response:
                return {'success': True, 'message': 'Call hung up'}
            else:
                return {'success': False, 'message': 'Failed to hangup'}
                
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()