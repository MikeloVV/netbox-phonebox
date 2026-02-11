from typing import Optional, Dict, Any
from .models import PBXServer, Extension, PhoneNumber, CallLog
from .asterisk_ami import AsteriskAMI
from .grandstream_ami import GrandstreamAMI
from django.utils import timezone


def get_ami_client(pbx_server: PBXServer):
    """
    Get appropriate AMI client based on PBX type
    
    Args:
        pbx_server: PBX server instance
    
    Returns:
        AMI client instance (AsteriskAMI or GrandstreamAMI)
    """
    if pbx_server.type == 'grandstream_ucm':
        return GrandstreamAMI(
            host=pbx_server.hostname,
            port=pbx_server.ami_port,
            username=pbx_server.ami_username,
            secret=pbx_server.ami_secret
        )
    else:
        # Для Asterisk, FreePBX и других
        return AsteriskAMI(
            host=pbx_server.hostname,
            port=pbx_server.ami_port,
            username=pbx_server.ami_username,
            secret=pbx_server.ami_secret
        )


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
        
        # Build channel name based on extension type and PBX type
        if pbx_server.type == 'grandstream_ucm':
            # Grandstream UCM использует PJSIP по умолчанию
            channel = f"PJSIP/{from_extension.extension}"
        elif from_extension.type == 'pjsip':
            channel = f"PJSIP/{from_extension.extension}"
        elif from_extension.type == 'sip':
            channel = f"SIP/{from_extension.extension}"
        else:
            channel = f"{from_extension.type.upper()}/{from_extension.extension}"
        
        # Get appropriate AMI client
        ami = get_ami_client(pbx_server)
        
        # Connect and originate call
        with ami:
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
        ami = get_ami_client(pbx_server)
        
        with ami:
            if ami.connected:
                return {
                    'success': True,
                    'online': True,
                    'pbx_type': pbx_server.get_type_display(),
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
        ami = get_ami_client(pbx_server)
        
        with ami:
            if pbx_server.type == 'grandstream_ucm' and hasattr(ami, 'get_active_channels'):
                result = ami.get_active_channels()
            else:
                result = ami.get_channel_status('')
            
            if result['success']:
                return result
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


def get_extension_status(pbx_server: PBXServer, extension: Extension) -> Dict[str, Any]:
    """
    Get extension status
    
    Args:
        pbx_server: PBX server
        extension: Extension to check
    
    Returns:
        Dict with extension status
    """
    try:
        ami = get_ami_client(pbx_server)
        
        with ami:
            if pbx_server.type == 'grandstream_ucm' and hasattr(ami, 'get_extension_status'):
                result = ami.get_extension_status(extension.extension)
            else:
                # Fallback to generic status check
                channel = f"PJSIP/{extension.extension}"
                result = ami.get_channel_status(channel)
            
            return result
                
    except Exception as e:
        return {
            'success': False,
            'message': f'Error: {str(e)}'
        }


def get_trunk_status(pbx_server: PBXServer, trunk_name: str) -> Dict[str, Any]:
    """
    Get SIP trunk status
    
    Args:
        pbx_server: PBX server
        trunk_name: Trunk name
    
    Returns:
        Dict with trunk status
    """
    try:
        ami = get_ami_client(pbx_server)
        
        with ami:
            if pbx_server.type == 'grandstream_ucm' and hasattr(ami, 'get_trunk_status'):
                result = ami.get_trunk_status(trunk_name)
            else:
                # Generic trunk status check
                result = {
                    'success': False,
                    'message': 'Trunk status check not implemented for this PBX type'
                }
            
            return result
                
    except Exception as e:
        return {
            'success': False,
            'message': f'Error: {str(e)}'
        }