from typing import Optional, Dict, Any
from .models import PBXServer, Extension, PhoneNumber, CallLog
from .asterisk_ami import AsteriskAMI
from django.utils import timezone


def make_call(pbx_server: PBXServer, from_extension: Extension, 
              to_number: str) -> Dict[str, Any]:
    """
    Initiate a call from extension to number
    
    Args:
        pbx_server: PBX server to use
        from_extension: Extension to originate from
        to_number: Number to call
    
    Returns:
        Dict with success status and message
    """
    try:
        # Normalize destination number
        if not to_number.startswith('+'):
            # Try to find PhoneNumber object
            phone = PhoneNumber.objects.filter(number=to_number).first()
            if phone:
                to_number = phone.normalized_number
        
        # Build channel name based on extension type
        if from_extension.type == 'pjsip':
            channel = f"PJSIP/{from_extension.extension}"
        elif from_extension.type == 'sip':
            channel = f"SIP/{from_extension.extension}"
        else:
            channel = f"{from_extension.type.upper()}/{from_extension.extension}"
        
        # Connect to AMI and originate call
        with AsteriskAMI(
            host=pbx_server.hostname,
            port=pbx_server.ami_port,
            username=pbx_server.ami_username,
            secret=pbx_server.ami_secret
        ) as ami:
            result = ami.originate_call(
                channel=channel,
                extension=to_number,
                caller_id=from_extension.extension,
                context='from-internal'
            )
            
            if result['success']:
                # Log the call attempt
                CallLog.objects.create(
                    call_id=f"manual_{timezone.now().timestamp()}",
                    pbx_server=pbx_server,
                    direction='outbound',
                    caller_number=from_extension.extension,
                    called_number=to_number,
                    extension=from_extension,
                    status='initiated',
                    start_time=timezone.now()
                )
            
            return result
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Error initiating call: {str(e)}'
        }


def get_pbx_status(pbx_server: PBXServer) -> Dict[str, Any]:
    """
    Get PBX server status
    
    Args:
        pbx_server: PBX server to check
    
    Returns:
        Dict with status information
    """
    try:
        with AsteriskAMI(
            host=pbx_server.hostname,
            port=pbx_server.ami_port,
            username=pbx_server.ami_username,
            secret=pbx_server.ami_secret
        ) as ami:
            if ami.connected:
                return {
                    'success': True,
                    'online': True,
                    'message': 'PBX is online'
                }
            else:
                return {
                    'success': False,
                    'online': False,
                    'message': 'Failed to connect to PBX'
                }
                
    except Exception as e:
        return {
            'success': False,
            'online': False,
            'message': f'Error: {str(e)}'
        }


def get_active_calls(pbx_server: PBXServer) -> Dict[str, Any]:
    """
    Get list of active calls on PBX
    
    Args:
        pbx_server: PBX server to query
    
    Returns:
        Dict with active calls information
    """
    try:
        with AsteriskAMI(
            host=pbx_server.hostname,
            port=pbx_server.ami_port,
            username=pbx_server.ami_username,
            secret=pbx_server.ami_secret
        ) as ami:
            result = ami.get_channel_status('')
            
            if result['success']:
                # Parse response to extract call information
                # This is simplified - actual parsing would be more complex
                return {
                    'success': True,
                    'calls': []  # Would contain parsed call data
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to get active calls'
                }
                
    except Exception as e:
        return {
            'success': False,
            'message': f'Error: {str(e)}'
        }