from django.db import migrations, models
import django.db.models.deletion
import taggit.managers
import utilities.json


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_phonebox', '0001_initial'),
        ('dcim', '__first__'),
        ('extras', '__first__'),
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
                ('name', models.CharField(help_text='PBX server name', max_length=100, unique=True)),
                ('type', models.CharField(
                    choices=[
                        ('asterisk', 'Asterisk'),
                        ('freepbx', 'FreePBX'),
                        ('3cx', '3CX'),
                        ('other', 'Other')
                    ],
                    default='asterisk',
                    help_text='PBX type',
                    max_length=20
                )),
                ('hostname', models.CharField(help_text='PBX hostname or IP address', max_length=255)),
                ('ami_port', models.IntegerField(default=5038, help_text='AMI port (default: 5038)')),
                ('ami_username', models.CharField(help_text='AMI username', max_length=100)),
                ('ami_secret', models.CharField(help_text='AMI secret/password', max_length=255)),
                ('web_url', models.URLField(blank=True, help_text='Web interface URL')),
                ('enabled', models.BooleanField(default=True, help_text='Enable this PBX server')),
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
                ('name', models.CharField(help_text='Trunk name', max_length=100, unique=True)),
                ('type', models.CharField(
                    choices=[
                        ('register', 'Register'),
                        ('peer', 'Peer'),
                        ('friend', 'Friend')
                    ],
                    default='peer',
                    help_text='SIP trunk type',
                    max_length=20
                )),
                ('host', models.CharField(help_text='SIP server hostname or IP', max_length=255)),
                ('port', models.IntegerField(default=5060, help_text='SIP port (default: 5060)')),
                ('transport', models.CharField(
                    choices=[
                        ('udp', 'UDP'),
                        ('tcp', 'TCP'),
                        ('tls', 'TLS'),
                        ('ws', 'WebSocket'),
                        ('wss', 'WebSocket Secure')
                    ],
                    default='udp',
                    help_text='Transport protocol',
                    max_length=10
                )),
                ('username', models.CharField(blank=True, help_text='SIP username', max_length=100)),
                ('secret', models.CharField(blank=True, help_text='SIP password', max_length=255)),
                ('context', models.CharField(default='from-trunk', help_text='Asterisk context', max_length=100)),
                ('enabled', models.BooleanField(default=True, help_text='Enable this trunk')),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('pbx_server', models.ForeignKey(
                    help_text='PBX server',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='sip_trunks',
                    to='netbox_phonebox.pbxserver'
                )),
                ('provider', models.ForeignKey(
                    blank=True,
                    help_text='Service provider',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='sip_trunks',
                    to='netbox_phonebox.telephonyprovider'
                )),
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
                ('extension', models.CharField(help_text='Extension number', max_length=20)),
                ('type', models.CharField(
                    choices=[
                        ('sip', 'SIP'),
                        ('pjsip', 'PJSIP'),
                        ('iax2', 'IAX2')
                    ],
                    default='pjsip',
                    help_text='Extension type',
                    max_length=10
                )),
                ('secret', models.CharField(blank=True, help_text='SIP secret/password', max_length=255)),
                ('enabled', models.BooleanField(default=True, help_text='Enable this extension')),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('pbx_server', models.ForeignKey(
                    help_text='PBX server',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='extensions',
                    to='netbox_phonebox.pbxserver'
                )),
                ('contact', models.ForeignKey(
                    blank=True,
                    help_text='Associated contact',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='extensions',
                    to='tenancy.contact'
                )),
                ('device', models.ForeignKey(
                    blank=True,
                    help_text='Associated device (IP Phone)',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='extensions',
                    to='dcim.device'
                )),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Extension',
                'verbose_name_plural': 'Extensions',
                'ordering': ['extension'],
            },
        ),
        
        # Call Log
        migrations.CreateModel(
            name='CallLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('call_id', models.CharField(help_text='Unique call ID from PBX', max_length=255, unique=True)),
                ('direction', models.CharField(
                    choices=[
                        ('inbound', 'Inbound'),
                        ('outbound', 'Outbound'),
                        ('internal', 'Internal')
                    ],
                    help_text='Call direction',
                    max_length=20
                )),
                ('caller_number', models.CharField(help_text='Caller phone number', max_length=50)),
                ('called_number', models.CharField(help_text='Called phone number', max_length=50)),
                ('status', models.CharField(
                    choices=[
                        ('answered', 'Answered'),
                        ('no_answer', 'No Answer'),
                        ('busy', 'Busy'),
                        ('failed', 'Failed'),
                        ('cancelled', 'Cancelled')
                    ],
                    help_text='Call status',
                    max_length=20
                )),
                ('start_time', models.DateTimeField(help_text='Call start time')),
                ('answer_time', models.DateTimeField(blank=True, help_text='Call answer time', null=True)),
                ('end_time', models.DateTimeField(blank=True, help_text='Call end time', null=True)),
                ('duration', models.IntegerField(default=0, help_text='Call duration in seconds')),
                ('recording_url', models.URLField(blank=True, help_text='Call recording URL')),
                ('comments', models.TextField(blank=True)),
                ('pbx_server', models.ForeignKey(
                    help_text='PBX server',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='call_logs',
                    to='netbox_phonebox.pbxserver'
                )),
                ('extension', models.ForeignKey(
                    blank=True,
                    help_text='Extension involved',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='call_logs',
                    to='netbox_phonebox.extension'
                )),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Call Log',
                'verbose_name_plural': 'Call Logs',
                'ordering': ['-start_time'],
            },
        ),
        
        # Add extension field to PhoneNumber
        migrations.AddField(
            model_name='phonenumber',
            name='extension',
            field=models.ForeignKey(
                blank=True,
                help_text='Associated extension',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='phone_numbers',
                to='netbox_phonebox.extension'
            ),
        ),
        
        # Unique constraint for Extension
        migrations.AlterUniqueTogether(
            name='extension',
            unique_together={('extension', 'pbx_server')},
        ),
        
        # Indexes for CallLog
        migrations.AddIndex(
            model_name='calllog',
            index=models.Index(fields=['-start_time'], name='netbox_phon_start_t_idx'),
        ),
        migrations.AddIndex(
            model_name='calllog',
            index=models.Index(fields=['caller_number'], name='netbox_phon_caller_idx'),
        ),
        migrations.AddIndex(
            model_name='calllog',
            index=models.Index(fields=['called_number'], name='netbox_phon_called_idx'),
        ),
        migrations.AddIndex(
            model_name='calllog',
            index=models.Index(fields=['status'], name='netbox_phon_status_cl_idx'),
        ),
    ]