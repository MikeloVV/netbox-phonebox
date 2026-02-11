from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_phonebox', '0002_phase2_pbx_integration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pbxserver',
            name='type',
            field=models.CharField(
                choices=[
                    ('asterisk', 'Asterisk'),
                    ('freepbx', 'FreePBX'),
                    ('grandstream_ucm', 'Grandstream UCM'),
                    ('3cx', '3CX'),
                    ('other', 'Other')
                ],
                default='asterisk',
                help_text='PBX type',
                max_length=20
            ),
        ),
    ]