from .asterisk_ami import AsteriskAMI
from typing import Dict, Any


class GrandstreamAMI(AsteriskAMI):
    """
    Grandstream UCM AMI client
    
    Grandstream UCM использует Asterisk AMI, но имеет некоторые особенности:
    - Другие имена каналов (по умолчанию PJSIP)
    - Специфичные контексты
    - Особенности в именовании транков
    """
    
    def __init__(self, host: str, port: int, username: str, secret: str):
        super().__init__(host, port, username, secret)
        self.pbx_type = 'grandstream_ucm'
    
    def originate_call(self, channel: str, extension: str, caller_id: str, 
                       context: str = 'from-internal', priority: int = 1) -> Dict[str, Any]:
        """
        Originate a call on Grandstream UCM
        
        Grandstream UCM особенности:
        - По умолчанию использует PJSIP
        - Контекст обычно 'from-internal' или 'from-extension'
        - Формат канала: PJSIP/extension
        
        Args:
            channel: Channel to call (e.g., 'PJSIP/100')
            extension: Extension to dial
            caller_id: Caller ID to use
            context: Dialplan context (default: 'from-internal')
            priority: Dialplan priority
        
        Returns:
            Dict with success status and message
        """
        
        # Grandstream UCM обычно использует PJSIP
        if not channel.startswith('PJSIP/') and not channel.startswith('SIP/'):
            channel = f"PJSIP/{channel}"
        
        # Используем родительский метод с адаптированными параметрами
        return super().originate_call(
            channel=channel,
            extension=extension,
            caller_id=caller_id,
            context=context,
            priority=priority
        )
    
    def get_extension_status(self, extension: str) -> Dict[str, Any]:
        """
        Get extension status on Grandstream UCM
        
        Args:
            extension: Extension number
        
        Returns:
            Dict with extension status information
        """
        try:
            if not self.connected:
                if not self.connect():
                    return {
                        'success': False,
                        'message': 'Not connected to PBX'
                    }
            
            # Проверяем статус PJSIP endpoint
            self._send_action('PJSIPShowEndpoint', {
                'Endpoint': extension
            })
            
            response = self._read_response()
            
            if 'Success' in response or 'DeviceState' in response:
                # Парсим статус
                status = 'unknown'
                if 'DeviceState: Not in use' in response:
                    status = 'available'
                elif 'DeviceState: In use' in response:
                    status = 'busy'
                elif 'DeviceState: Unavailable' in response:
                    status = 'offline'
                
                return {
                    'success': True,
                    'extension': extension,
                    'status': status,
                    'response': response
                }
            else:
                return {
                    'success': False,
                    'message': 'Extension not found'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
    
    def get_trunk_status(self, trunk_name: str) -> Dict[str, Any]:
        """
        Get SIP trunk status on Grandstream UCM
        
        Args:
            trunk_name: Trunk name
        
        Returns:
            Dict with trunk status information
        """
        try:
            if not self.connected:
                if not self.connect():
                    return {
                        'success': False,
                        'message': 'Not connected to PBX'
                    }
            
            # Проверяем статус PJSIP trunk
            self._send_action('PJSIPShowEndpoint', {
                'Endpoint': trunk_name
            })
            
            response = self._read_response()
            
            if 'Success' in response:
                # Определяем статус регистрации
                registered = 'Registered' in response or 'Qualified' in response
                
                return {
                    'success': True,
                    'trunk': trunk_name,
                    'registered': registered,
                    'response': response
                }
            else:
                return {
                    'success': False,
                    'message': 'Trunk not found'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
    
    def get_active_channels(self) -> Dict[str, Any]:
        """
        Get list of active channels on Grandstream UCM
        
        Returns:
            Dict with active channels information
        """
        try:
            if not self.connected:
                if not self.connect():
                    return {
                        'success': False,
                        'message': 'Not connected to PBX'
                    }
            
            self._send_action('CoreShowChannels')
            response = self._read_response()
            
            if 'Success' in response:
                # Парсим активные каналы
                channels = []
                lines = response.split('\r\n')
                
                for line in lines:
                    if 'Channel:' in line:
                        channel_info = {}
                        # Простой парсинг (можно улучшить)
                        for detail_line in lines[lines.index(line):]:
                            if detail_line.strip() == '':
                                break
                            if ':' in detail_line:
                                key, value = detail_line.split(':', 1)
                                channel_info[key.strip()] = value.strip()
                        
                        if channel_info:
                            channels.append(channel_info)
                
                return {
                    'success': True,
                    'channels': channels,
                    'count': len(channels)
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to get channels'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
    
    def park_call(self, channel: str, parking_lot: str = 'default') -> Dict[str, Any]:
        """
        Park a call (Grandstream UCM feature)
        
        Args:
            channel: Channel to park
            parking_lot: Parking lot name
        
        Returns:
            Dict with success status
        """
        try:
            if not self.connected:
                if not self.connect():
                    return {
                        'success': False,
                        'message': 'Not connected to PBX'
                    }
            
            self._send_action('Park', {
                'Channel': channel,
                'ParkingLot': parking_lot
            })
            
            response = self._read_response()
            
            if 'Success' in response:
                return {
                    'success': True,
                    'message': 'Call parked successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to park call'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }