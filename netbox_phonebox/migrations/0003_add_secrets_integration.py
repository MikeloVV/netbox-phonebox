from django.db import migrations, models
import django.db.models.deletion


def check_secrets_available(apps, schema_editor):
    """Check if netbox-secrets is installed"""
    try:
        from netbox_secrets.models import Secret
        return True
    except ImportError:
        return False


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_phonebox', '0002_phase2_pbx_integration'),
    ]

    operations = []
    
    # Only add fields if netbox-secrets is available
    try:
        from netbox_secrets.models import Secret
        
        operations.extend([
            # PBXServer - добавить ami_secret_ref
            migrations.AddField(
                model_name='pbxserver',
                name='ami_secret_ref',
                field=models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='pbx_servers',
                    to='netbox_secrets.secret',
                    help_text='AMI secret from NetBox Secrets',
                    verbose_name='AMI Secret Reference'
                ),
            ),
            
            # SIPTrunk - добавить secret_ref
            migrations.AddField(
                model_name='siptrunk',
                name='secret_ref',
                field=models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='sip_trunks',
                    to='netbox_secrets.secret',
                    help_text='SIP secret from NetBox Secrets',
                    verbose_name='Secret Reference'
                ),
            ),
            
            # Extension - добавить secret_ref
            migrations.AddField(
                model_name='extension',
                name='secret_ref',
                field=models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='extensions',
                    to='netbox_secrets.secret',
                    help_text='Extension secret from NetBox Secrets',
                    verbose_name='Secret Reference'
                ),
            ),
        ])
    except ImportError:
        # netbox-secrets not installed, skip these fields
        pass