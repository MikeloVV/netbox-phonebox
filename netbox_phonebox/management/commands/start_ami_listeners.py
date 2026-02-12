from django.core.management.base import BaseCommand
from netbox_phonebox.ami_listener import ami_listener_manager
import signal
import sys
import time


class Command(BaseCommand):
    help = 'Start AMI event listeners for automatic CDR import'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--pbx-id',
            type=int,
            help='Start listener only for specific PBX server ID'
        )
    
    def handle(self, *args, **options):
        pbx_id = options.get('pbx_id')
        
        # Setup signal handlers for graceful shutdown
        def signal_handler(sig, frame):
            self.stdout.write(self.style.WARNING('\nShutting down listeners...'))
            ami_listener_manager.stop_all()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start listeners
        if pbx_id:
            from netbox_phonebox.models import PBXServer
            try:
                pbx = PBXServer.objects.get(pk=pbx_id)
                self.stdout.write(f'Starting listener for {pbx.name}...')
                ami_listener_manager.start_listener(pbx)
            except PBXServer.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'PBX server with ID {pbx_id} not found'))
                return
        else:
            self.stdout.write('Starting listeners for all enabled PBX servers...')
            ami_listener_manager.start_all()
        
        # Show status
        status = ami_listener_manager.get_status()
        self.stdout.write(self.style.SUCCESS(f'\nStarted {len(status)} listener(s):'))
        for pbx_id, info in status.items():
            self.stdout.write(f"  - {info['pbx_name']}: {'Running' if info['running'] else 'Stopped'}")
        
        # Keep running
        self.stdout.write('\nListeners are running. Press Ctrl+C to stop.\n')
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nShutting down...'))
            ami_listener_manager.stop_all()