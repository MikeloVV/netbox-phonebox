from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_phonebox', '0003_add_grandstream_ucm'),
    ]

    operations = [
        # Сделать ami_secret необязательным
        migrations.AlterField(
            model_name='pbxserver',
            name='ami_secret',
            field=models.CharField(
                max_length=255,
                blank=True,
                default='',
                help_text='AMI secret/password (deprecated - use ami_secret_ref instead)'
            ),
        ),
        
        # Сделать secret необязательным для SIPTrunk
        migrations.AlterField(
            model_name='siptrunk',
            name='secret',
            field=models.CharField(
                max_length=255,
                blank=True,
                default='',
                help_text='SIP secret/password (deprecated - use secret_ref instead)'
            ),
        ),
        
        # Сделать secret необязательным для Extension
        migrations.AlterField(
            model_name='extension',
            name='secret',
            field=models.CharField(
                max_length=255,
                blank=True,
                default='',
                help_text='Extension secret/password (deprecated - use secret_ref instead)'
            ),
        ),
    ]