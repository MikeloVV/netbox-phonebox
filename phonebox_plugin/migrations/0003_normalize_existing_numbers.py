from django.db import migrations
import phonenumbers
from phonenumbers import NumberParseException


def normalize_existing_numbers(apps, schema_editor):
    """Normalize existing phone numbers"""
    PhoneNumber = apps.get_model('netbox_phonebox', 'PhoneNumber')
    
    for phone in PhoneNumber.objects.all():
        try:
            # Пытаемся распарсить номер
            parsed = phonenumbers.parse(phone.number, phone.country_code or None)
            
            if phonenumbers.is_valid_number(parsed):
                # Нормализуем
                phone.normalized_number = phonenumbers.format_number(
                    parsed,
                    phonenumbers.PhoneNumberFormat.E164
                )
                
                # Определяем страну
                if not phone.country_code:
                    phone.country_code = phonenumbers.region_code_for_number(parsed)
                
                phone.save(update_fields=['normalized_number', 'country_code'])
            else:
                print(f"Invalid number: {phone.number} (ID: {phone.pk})")
        except NumberParseException as e:
            print(f"Cannot parse number: {phone.number} (ID: {phone.pk}) - {e}")
            # Оставляем как есть, но устанавливаем normalized_number = number
            phone.normalized_number = phone.number
            phone.save(update_fields=['normalized_number'])


def reverse_normalize(apps, schema_editor):
    """Reverse migration - clear normalized numbers"""
    PhoneNumber = apps.get_model('netbox_phonebox', 'PhoneNumber')
    PhoneNumber.objects.all().update(normalized_number='', country_code='')


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_phonebox', '0002_add_normalization'),
    ]

    operations = [
        migrations.RunPython(normalize_existing_numbers, reverse_normalize),
    ]