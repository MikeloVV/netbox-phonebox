import threading
import time
import logging
from django.utils import timezone
from datetime import datetime
from .asterisk_ami import AsteriskAMI
from .grandstream_ami import GrandstreamAMI
from .models import PBXServer, CallLog, Extension

logger = logging.getLogger('netbox_phonebox.ami_listener')


class AMIEventListener:
    """
    AMI Event Listener for automatic CDR import
    
    Listens to AMI events and creates CallLog entries automatically
    """
    
    def __init__(self, pbx_server: PBXServer):
        self.pbx_server = pbx_server
        self.ami = None
        self.running = False
        self.thread = None
        self.call_cache = {}  # Cache for tracking calls
        
    def start(self):
        """Start listening to AMI events"""
        if self.running:
            logger.warning(f"Listener already running for {self.pbx_server.name}")
            return
        
        logger.info(f"Starting AMI event listener for {self.pbx_server.name}")
        self.running = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop listening to AMI events"""
        logger.info(f"Stopping AMI event listener for {self.pbx_server.name}")
        self.running = False
        
        if self.ami:
            try:
                self.ami.disconnect()
            except:
                pass
        
        if self.thread:
            self.thread.join(timeout=5)
    
    def _listen_loop(self):
        """Main listening loop"""
        while self.running:
            try:
                # Connect to AMI
                if self.pbx_server.type == 'grandstream_ucm':
                    self.ami = GrandstreamAMI(
                        host=self.pbx_server.hostname,
                        port=self.pbx_server.ami_port,
                        username=self.pbx_server.ami_username,
                        secret=self.pbx_server.ami_secret
                    )
                else:
                    self.ami = AsteriskAMI(
                        host=self.pbx_server.hostname,
                        port=self.pbx_server.ami_port,
                        username=self.pbx_server.ami_username,
                        secret=self.pbx_server.ami_secret
                    )
                
                if not self.ami.connect():
                    logger.error(f"Failed to connect to {self.pbx_server.name}")
                    time.sleep(30)  # Wait before retry
                    continue
                
                logger.info(f"Connected to {self.pbx_server.name}, listening for events...")
                
                # Listen for events
                while self.running and self.ami.connected:
                    try:
                        event = self._read_event()
                        if event:
                            self._process_event(event)
                    except Exception as e:
                        logger.error(f"Error processing event: {e}", exc_info=True)
                        break
                
            except Exception as e:
                logger.error(f"Error in listen loop: {e}", exc_info=True)
            finally:
                if self.ami:
                    try:
                        self.ami.disconnect()
                    except:
                        pass
                
                if self.running:
                    logger.info("Reconnecting in 30 seconds...")
                    time.sleep(30)
    
    def _read_event(self):
        """Read an AMI event"""
        if not self.ami or not self.ami.socket:
            return None
        
        try:
            self.ami.socket.settimeout(60)  # 60 second timeout
            event_data = ""
            
            while True:
                data = self.ami.socket.recv(4096)
                if not data:
                    return None
                
                chunk = data.decode('utf-8', errors='ignore')
                event_data += chunk
                
                # Event ends with double newline
                if '\r\n\r\n' in event_data:
                    break
            
            # Parse event
            event = self._parse_event(event_data)
            return event
            
        except Exception as e:
            logger.debug(f"Error reading event: {e}")
            return None
    
    def _parse_event(self, event_data: str) -> dict:
        """Parse AMI event data into dict"""
        event = {}
        
        for line in event_data.split('\r\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                event[key.strip()] = value.strip()
        
        return event
    
    def _process_event(self, event: dict):
        """Process AMI event and create CallLog if needed"""
        event_type = event.get('Event', '')
        
        # Log interesting events
        if event_type in ['Newchannel', 'Newstate', 'Hangup', 'Cdr', 'HangupRequest']:
            logger.debug(f"Event: {event_type} - {event.get('Channel', 'N/A')}")
        
        # Process based on event type
        if event_type == 'Newchannel':
            self._handle_newchannel(event)
        elif event_type == 'Hangup':
            self._handle_hangup(event)
        elif event_type == 'Cdr':
            self._handle_cdr(event)
    
    def _handle_newchannel(self, event: dict):
        """Handle new channel event (call start)"""
        channel = event.get('Channel', '')
        uniqueid = event.get('Uniqueid', '')
        callerid = event.get('CallerIDNum', '')
        
        if not uniqueid:
            return
        
        # Cache call info
        self.call_cache[uniqueid] = {
            'channel': channel,
            'caller': callerid,
            'start_time': timezone.now(),
            'event': event
        }
        
        logger.debug(f"New call: {uniqueid} from {callerid}")
    
    def _handle_hangup(self, event: dict):
        """Handle hangup event (call end)"""
        uniqueid = event.get('Uniqueid', '')
        
        if uniqueid in self.call_cache:
            call_info = self.call_cache[uniqueid]
            call_info['end_time'] = timezone.now()
            call_info['hangup_event'] = event
            
            logger.debug(f"Call ended: {uniqueid}")
    
    def _handle_cdr(self, event: dict):
        """Handle CDR event - create CallLog entry"""
        try:
            # Extract CDR data
            uniqueid = event.get('UniqueID', '')
            src = event.get('Source', event.get('Src', ''))
            dst = event.get('Destination', event.get('Dst', ''))
            duration = int(event.get('Duration', 0))
            billsec = int(event.get('BillableSeconds', event.get('BillSec', 0)))
            disposition = event.get('Disposition', 'NO ANSWER')
            start_time_str = event.get('StartTime', '')
            answer_time_str = event.get('AnswerTime', '')
            end_time_str = event.get('EndTime', '')
            
            # Determine direction
            direction = 'internal'
            if src.startswith('+') or len(src) > 6:
                direction = 'inbound'
            elif dst.startswith('+') or len(dst) > 6:
                direction = 'outbound'
            
            # Map disposition to status
            status_map = {
                'ANSWERED': 'answered',
                'NO ANSWER': 'no_answer',
                'BUSY': 'busy',
                'FAILED': 'failed',
                'CONGESTION': 'failed'
            }
            status = status_map.get(disposition, 'no_answer')
            
            # Parse timestamps
            start_time = self._parse_timestamp(start_time_str) or timezone.now()
            answer_time = self._parse_timestamp(answer_time_str)
            end_time = self._parse_timestamp(end_time_str)
            
            # Find extension
            extension = None
            if direction == 'outbound':
                extension = Extension.objects.filter(
                    pbx_server=self.pbx_server,
                    extension=src
                ).first()
            elif direction == 'inbound':
                extension = Extension.objects.filter(
                    pbx_server=self.pbx_server,
                    extension=dst
                ).first()
            
            # Create CallLog
            call_log = CallLog.objects.create(
                call_id=uniqueid,
                pbx_server=self.pbx_server,
                direction=direction,
                caller_number=src,
                called_number=dst,
                extension=extension,
                status=status,
                start_time=start_time,
                answer_time=answer_time,
                end_time=end_time,
                duration=billsec,  # Use billable seconds
                comments=f"Auto-imported from AMI CDR event"
            )
            
            logger.info(f"Created CallLog: {call_log.call_id} - {src} -> {dst} ({status})")
            
            # Clean up cache
            if uniqueid in self.call_cache:
                del self.call_cache[uniqueid]
            
        except Exception as e:
            logger.error(f"Error creating CallLog from CDR: {e}", exc_info=True)
    
    def _parse_timestamp(self, timestamp_str: str):
        """Parse timestamp from CDR event"""
        if not timestamp_str:
            return None
        
        try:
            # Try different formats
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%S.%f',
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(timestamp_str, fmt)
                    return timezone.make_aware(dt)
                except ValueError:
                    continue
            
            return None
        except Exception as e:
            logger.debug(f"Error parsing timestamp '{timestamp_str}': {e}")
            return None


class AMIListenerManager:
    """Manager for multiple AMI listeners"""
    
    _instance = None
    _listeners = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def start_listener(self, pbx_server: PBXServer):
        """Start listener for a PBX server"""
        if not pbx_server.enabled:
            logger.info(f"PBX {pbx_server.name} is disabled, not starting listener")
            return
        
        if pbx_server.pk in self._listeners:
            logger.info(f"Listener already running for {pbx_server.name}")
            return
        
        listener = AMIEventListener(pbx_server)
        listener.start()
        self._listeners[pbx_server.pk] = listener
        
        logger.info(f"Started listener for {pbx_server.name}")
    
    def stop_listener(self, pbx_server: PBXServer):
        """Stop listener for a PBX server"""
        if pbx_server.pk in self._listeners:
            listener = self._listeners[pbx_server.pk]
            listener.stop()
            del self._listeners[pbx_server.pk]
            logger.info(f"Stopped listener for {pbx_server.name}")
    
    def restart_listener(self, pbx_server: PBXServer):
        """Restart listener for a PBX server"""
        self.stop_listener(pbx_server)
        time.sleep(1)
        self.start_listener(pbx_server)
    
    def start_all(self):
        """Start listeners for all enabled PBX servers"""
        from .models import PBXServer
        
        for pbx in PBXServer.objects.filter(enabled=True):
            self.start_listener(pbx)
    
    def stop_all(self):
        """Stop all listeners"""
        for listener in list(self._listeners.values()):
            listener.stop()
        self._listeners.clear()
    
    def get_status(self):
        """Get status of all listeners"""
        status = {}
        for pbx_id, listener in self._listeners.items():
            status[pbx_id] = {
                'running': listener.running,
                'connected': listener.ami.connected if listener.ami else False,
                'pbx_name': listener.pbx_server.name
            }
        return status


# Global manager instance
ami_listener_manager = AMIListenerManager()