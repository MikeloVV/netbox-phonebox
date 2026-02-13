from django.db import migrations, models
import django.db.models.deletion
import taggit.managers
import utilities.json


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dcim', '0001_initial'),
        ('virtualization', '0001_initial'),
        ('tenancy', '0001_initial'),
        ('extras', '0001_initial'),
    ]

    operations = [
        # Phone Number
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('number', models.CharField(help_text='Phone number in E.164 format', max_length=20, unique=True)),
                ('type', models.CharField(choices=[('mobile', 'Mobile'), ('landline', 'Landline'), ('voip', 'VoIP'), ('fax', 'Fax'), ('toll_free', 'Toll Free')], default='mobile', max_length=20)),
                ('status', models.CharField(choices=[('active', 'Active'), ('reserved', 'Reserved'), ('inactive', 'Inactive')], default='active', max_length=20)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='phone_numbers', to='tenancy.contact')),
                ('device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='phone_numbers', to='dcim.device')),
                ('virtual_machine', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='phone_numbers', to='virtualization.virtualmachine')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Phone Number',
                'verbose_name_plural': 'Phone Numbers',
                'ordering': ['number'],
            },
        ),
        
        # Telephony Provider
        migrations.CreateModel(
            name='TelephonyProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('website', models.URLField(blank=True)),
                ('support_phone', models.CharField(blank=True, max_length=50)),
                ('support_email', models.EmailField(blank=True, max_length=254)),
                ('comments', models.TextField(blank=True)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Telephony Provider',
                'verbose_name_plural': 'Telephony Providers',
                'ordering': ['name'],
            },
        ),
        
        # Add provider FK to PhoneNumber
        migrations.AddField(
            model_name='phonenumber',
            name='provider',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='phone_numbers', to='netbox_phonebox.telephonyprovider'),
        ),
    ]