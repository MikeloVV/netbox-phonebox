from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_phonebox', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='phonenumber',
            name='normalized_number',
            field=models.CharField(
                default='',
                editable=False,
                help_text='Normalized E.164 format (auto-generated)',
                max_length=20
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='phonenumber',
            name='country_code',
            field=models.CharField(
                blank=True,
                help_text='Country code (e.g., RU, US, GB). Auto-detected if not provided.',
                max_length=5
            ),
        ),
        migrations.AlterField(
            model_name='phonenumber',
            name='number',
            field=models.CharField(
                help_text='Phone number (will be normalized to E.164 format)',
                max_length=50
            ),
        ),
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