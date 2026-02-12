from django.core.management.base import BaseCommand
from netbox_phonebox.models import PBXServer, SIPTrunk, Extension, SECRETS_AVAILABLE

if SECRETS_AVAILABLE:
    from netbox_secrets.models import Secret, SecretRole


class Command(BaseCommand):
    help = 'Migrate existing secrets to NetBox Secrets plugin'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually migrating'
        )
        
        parser.add_argument(
            '--role',
            type=str,
            default='phonebox',
            help='Secret role name to use (default: phonebox)'
        )
    
    def handle(self, *args, **options):
        if not SECRETS_AVAILABLE:
            self.stdout.write(self.style.ERROR('NetBox Secrets plugin is not installed'))
            return
        
        dry_run = options['dry_run']
        role_name = options['role']
        
        # Get or create SecretRole
        role, created = SecretRole.objects.get_or_create(
            name=role_name,
            defaults={'description': 'PhoneBox secrets (PBX, SIP, Extensions)'}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created SecretRole: {role.name}'))
        
        migrated_count = 0
        
        # Migrate PBX Server secrets
        self.stdout.write('\nMigrating PBX Server secrets...')
        for pbx in PBXServer.objects.filter(ami_secret__isnull=False).exclude(ami_secret=''):
            if hasattr(pbx, 'ami_secret_ref') and pbx.ami_secret_ref:
                self.stdout.write(f'  - {pbx.name}: Already migrated')
                continue
            
            if dry_run:
                self.stdout.write(f'  - {pbx.name}: Would migrate AMI secret')
            else:
                secret = Secret.objects.create(
                    role=role,
                    name=f'{pbx.name} AMI Secret',
                    plaintext=pbx.ami_secret
                )
                pbx.ami_secret_ref = secret
                pbx.ami_secret = ''  # Clear old secret
                pbx.save()
                self.stdout.write(self.style.SUCCESS(f'  - {pbx.name}: Migrated'))
                migrated_count += 1
        
        # Migrate SIP Trunk secrets
        self.stdout.write('\nMigrating SIP Trunk secrets...')
        for trunk in SIPTrunk.objects.filter(secret__isnull=False).exclude(secret=''):
            if hasattr(trunk, 'secret_ref') and trunk.secret_ref:
                self.stdout.write(f'  - {trunk.name}: Already migrated')
                continue
            
            if dry_run:
                self.stdout.write(f'  - {trunk.name}: Would migrate SIP secret')
            else:
                secret = Secret.objects.create(
                    role=role,
                    name=f'{trunk.name} SIP Secret',
                    plaintext=trunk.secret
                )
                trunk.secret_ref = secret
                trunk.secret = ''  # Clear old secret
                trunk.save()
                self.stdout.write(self.style.SUCCESS(f'  - {trunk.name}: Migrated'))
                migrated_count += 1
        
        # Migrate Extension secrets
        self.stdout.write('\nMigrating Extension secrets...')
        for ext in Extension.objects.filter(secret__isnull=False).exclude(secret=''):
            if hasattr(ext, 'secret_ref') and ext.secret_ref:
                self.stdout.write(f'  - {ext.extension}: Already migrated')
                continue
            
            if dry_run:
                self.stdout.write(f'  - {ext.extension}: Would migrate extension secret')
            else:
                secret = Secret.objects.create(
                    role=role,
                    name=f'Extension {ext.extension} Secret',
                    plaintext=ext.secret
                )
                ext.secret_ref = secret
                ext.secret = ''  # Clear old secret
                ext.save()
                self.stdout.write(self.style.SUCCESS(f'  - {ext.extension}: Migrated'))
                migrated_count += 1
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f'\nDry run completed. {migrated_count} secrets would be migrated.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\nMigration completed. {migrated_count} secrets migrated.'))