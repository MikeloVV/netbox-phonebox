from django.db import migrations, models
import django.db.models.deletion
import taggit.managers
import utilities.json


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dcim', '__first__'),
        ('virtualization', '__first__'),
        ('tenancy', '__first__'),
        ('extras', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='TelephonyProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('name', models.CharField(help_text='Provider name', max_length=100, unique=True)),
                ('description', models.CharField(blank=True, help_text='Provider description', max_length=200)),
                ('website', models.URLField(blank=True, help_text='Provider website')),
                ('support_phone', models.CharField(blank=True, help_text='Support phone number', max_length=50)),
                ('support_email', models.EmailField(blank=True, help_text='Support email', max_length=254)),
                ('comments', models.TextField(blank=True)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Telephony Provider',
                'verbose_name_plural': 'Telephony Providers',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('number', models.CharField(help_text='Phone number (will be normalized to E.164 format)', max_length=50)),
                ('normalized_number', models.CharField(db_index=True, editable=False, help_text='Normalized E.164 format (auto-generated)', max_length=20)),
                ('country_code', models.CharField(blank=True, help_text='Country code (e.g., RU, US, GB). Auto-detected if not provided.', max_length=5)),
                ('type', models.CharField(
                    choices=[
                        ('mobile', 'Mobile'),
                        ('landline', 'Landline'),
                        ('voip', 'VoIP'),
                        ('fax', 'Fax'),
                        ('emergency', 'Emergency'),
                        ('toll_free', 'Toll-Free')
                    ],
                    default='mobile',
                    help_text='Phone number type',
                    max_length=20
                )),
                ('status', models.CharField(
                    choices=[
                        ('active', 'Active'),
                        ('reserved', 'Reserved'),
                        ('deprecated', 'Deprecated')
                    ],
                    default='active',
                    help_text='Phone number status',
                    max_length=20
                )),
                ('description', models.CharField(blank=True, help_text='Description', max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('contact', models.ForeignKey(
                    blank=True,
                    help_text='Associated contact',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='phone_numbers',
                    to='tenancy.contact'
                )),
                ('device', models.ForeignKey(
                    blank=True,
                    help_text='Associated device',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='phone_numbers',
                    to='dcim.device'
                )),
                ('provider', models.ForeignKey(
                    blank=True,
                    help_text='Service provider',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='phone_numbers',
                    to='netbox_phonebox.telephonyprovider'
                )),
                ('virtual_machine', models.ForeignKey(
                    blank=True,
                    help_text='Associated virtual machine',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='phone_numbers',
                    to='virtualization.virtualmachine'
                )),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Phone Number',
                'verbose_name_plural': 'Phone Numbers',
                'ordering': ['normalized_number'],
            },
        ),
        # Indexes
        migrations.AddIndex(
            model_name='phonenumber',
            index=models.Index(fields=['normalized_number'], name='netbox_phon_normali_idx'),
        ),
        migrations.AddIndex(
            model_name='phonenumber',
            index=models.Index(fields=['country_code'], name='netbox_phon_country_idx'),
        ),
        migrations.AddIndex(
            model_name='phonenumber',
            index=models.Index(fields=['type'], name='netbox_phon_type_idx'),
        ),
        migrations.AddIndex(
            model_name='phonenumber',
            index=models.Index(fields=['status'], name='netbox_phon_status_idx'),
        ),
    ]