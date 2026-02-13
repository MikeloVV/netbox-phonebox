from django.db import migrations, models
import django.db.models.deletion
import taggit.managers
import utilities.json


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_phonebox', '0001_initial'),
        ('tenancy', '0001_initial'),
        ('dcim', '0001_initial'),
    ]

    operations = [
        # PBX Server
        migrations.CreateModel(
            name='PBXServer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('type', models.CharField(choices=[('asterisk', 'Asterisk'), ('freepbx', 'FreePBX'), ('grandstream_ucm', 'Grandstream UCM'), ('3cx', '3CX'), ('other', 'Other')], default='asterisk', max_length=20)),
                ('hostname', models.CharField(max_length=255)),
                ('ami_port', models.PositiveIntegerField(default=5038)),
                ('ami_username', models.CharField(max_length=100)),
                ('ami_secret', models.CharField(blank=True, default='', max_length=255)),
                ('web_url', models.URLField(blank=True)),
                ('enabled', models.BooleanField(default=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'PBX Server',
                'verbose_name_plural': 'PBX Servers',
                'ordering': ['name'],
            },
        ),
        
        # SIP Trunk
        migrations.CreateModel(
            name='SIPTrunk',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('peer', 'Peer'), ('user', 'User'), ('friend', 'Friend')], default='peer', max_length=10)),
                ('host', models.CharField(max_length=255)),
                ('port', models.PositiveIntegerField(default=5060)),
                ('transport', models.CharField(choices=[('udp', 'UDP'), ('tcp', 'TCP'), ('tls', 'TLS'), ('ws', 'WebSocket'), ('wss', 'WebSocket Secure')], default='udp', max_length=10)),
                ('username', models.CharField(blank=True, max_length=100)),
                ('secret', models.CharField(blank=True, default='', max_length=255)),
                ('context', models.CharField(default='from-trunk', max_length=100)),
                ('enabled', models.BooleanField(default=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('pbx_server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sip_trunks', to='netbox_phonebox.pbxserver')),
                ('provider', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sip_trunks', to='netbox_phonebox.telephonyprovider')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'SIP Trunk',
                'verbose_name_plural': 'SIP Trunks',
                'ordering': ['name'],
            },
        ),
        
        # Extension
        migrations.CreateModel(
            name='Extension',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('extension', models.CharField(max_length=20)),
                ('type', models.CharField(choices=[('pjsip', 'PJSIP'), ('sip', 'SIP'), ('iax2', 'IAX2')], default='pjsip', max_length=10)),
                ('secret', models.CharField(blank=True, default='', max_length=255)),
                ('enabled', models.BooleanField(default=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('pbx_server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='extensions', to='netbox_phonebox.pbxserver')),
                ('contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='extensions', to='tenancy.contact')),
                ('device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='extensions', to='dcim.device')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Extension',
                'verbose_name_plural': 'Extensions',
                'ordering': ['extension'],
            },
        ),
        
        # CallLog
        migrations.CreateModel(
            name='CallLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('call_id', models.CharField(max_length=100, unique=True)),
                ('direction', models.CharField(choices=[('inbound', 'Inbound'), ('outbound', 'Outbound'), ('internal', 'Internal')], max_length=10)),
                ('caller_number', models.CharField(max_length=50)),
                ('called_number', models.CharField(max_length=50)),
                ('status', models.CharField(choices=[('answered', 'Answered'), ('no_answer', 'No Answer'), ('busy', 'Busy'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], max_length=20)),
                ('start_time', models.DateTimeField()),
                ('answer_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('duration', models.PositiveIntegerField(default=0)),
                ('recording_url', models.URLField(blank=True)),
                ('comments', models.TextField(blank=True)),
                ('pbx_server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='call_logs', to='netbox_phonebox.pbxserver')),
                ('extension', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='call_logs', to='netbox_phonebox.extension')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Call Log',
                'verbose_name_plural': 'Call Logs',
                'ordering': ['-start_time'],
            },
        ),
        
        # Add extension FK to PhoneNumber
        migrations.AddField(
            model_name='phonenumber',
            name='extension',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='phone_numbers', to='netbox_phonebox.extension'),
        ),
        
        # Add unique constraints
        migrations.AddConstraint(
            model_name='siptrunk',
            constraint=models.UniqueConstraint(fields=['pbx_server', 'name'], name='unique_siptrunk_per_pbx'),
        ),
        migrations.AddConstraint(
            model_name='extension',
            constraint=models.UniqueConstraint(fields=['pbx_server', 'extension'], name='unique_extension_per_pbx'),
        ),
    ]