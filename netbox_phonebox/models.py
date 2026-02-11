from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from netbox.models import NetBoxModel
from dcim.models import Device
from virtualization.models import VirtualMachine
from tenancy.models import Contact
import phonenumbers
from phonenumbers import NumberParseException
from datetime import datetime


class Provider(NetBoxModel):
    """Telephone service provider"""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text='Provider name'
    )
    
    description = models.CharField(
        max_length=200,
        blank=True,
        help_text='Provider description'
    )
    
    website = models.URLField(
        blank=True,
        help_text='Provider website'
    )
    
    support_phone = models.CharField(
        max_length=50,
        blank=True,
        help_text='Support phone number'
    )
    
    support_email = models.EmailField(
        blank=True,
        help_text='Support email'
    )
    
    comments = models.TextField(
        blank=True
    )
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('plugins:netbox_phonebox:provider', args=[self.pk])
    
    @property
    def numbers_count(self):
        """Count of phone numbers"""
        return self.phone_numbers.count()


class PhoneNumber(NetBoxModel):
    """Phone number model with validation and normalization"""
    
    TYPE_CHOICES = [
        ('mobile', 'Mobile'),
        ('landline', 'Landline'),
        ('voip', 'VoIP'),
        ('fax', 'Fax'),
        ('emergency', 'Emergency'),
        ('toll_free', 'Toll-Free'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('reserved', 'Reserved'),
        ('deprecated', 'Deprecated'),
    ]
    
    number = models.CharField(
        max_length=50,
        help_text='Phone number (will be normalized to E.164 format)'
    )
    
    normalized_number = models.CharField(
        max_length=20,
        editable=False,
        db_index=True,
        help_text='Normalized E.164 format (auto-generated)'
    )
    
    country_code = models.CharField(
        max_length=5,
        blank=True,
        help_text='Country code (e.g., RU, US, GB). Auto-detected if not provided.'
    )
    
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='mobile',
        help_text='Phone number type'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text='Phone number status'
    )
    
    provider = models.ForeignKey(
        Provider,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='phone_numbers',
        help_text='Service provider'
    )
    
    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='phone_numbers',
        help_text='Associated contact'
    )
    
    device = models.ForeignKey(
        Device,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='phone_numbers',
        help_text='Associated device'
    )
    
    virtual_machine = models.ForeignKey(
        VirtualMachine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='phone_numbers',
        help_text='Associated virtual machine'
    )
    
    description = models.CharField(
        max_length=200,
        blank=True,
        help_text='Description'
    )
    
    comments = models.TextField(
        blank=True
    )
    
    class Meta:
        ordering = ['normalized_number']
        indexes = [
            models.Index(fields=['normalized_number']),
            models.Index(fields=['country_code']),
            models.Index(fields=['type']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return self.formatted_international or self.number
    
    def get_absolute_url(self):
        return reverse('plugins:netbox_phonebox:phonenumber', args=[self.pk])
    
    def clean(self):
        """Validate and normalize phone number"""
        super().clean()
        
        if not self.number:
            raise ValidationError({'number': 'Phone number is required'})
        
        try:
            # Пытаемся распарсить номер
            # Если указан country_code, используем его
            region = self.country_code if self.country_code else None
            
            parsed = phonenumbers.parse(self.number, region)
            
            # Проверяем валидность
            if not phonenumbers.is_valid_number(parsed):
                raise ValidationError({
                    'number': f'Invalid phone number format. Please use international format (e.g., +1234567890)'
                })
            
            # Нормализуем в E.164
            self.normalized_number = phonenumbers.format_number(
                parsed,
                phonenumbers.PhoneNumberFormat.E164
            )
            
            # Определяем или проверяем страну
            detected_country = phonenumbers.region_code_for_number(parsed)
            
            if not self.country_code:
                self.country_code = detected_country
            elif self.country_code != detected_country:
                # Предупреждение, если указанная страна не совпадает с обнаруженной
                raise ValidationError({
                    'country_code': f'Country code mismatch. Number appears to be from {detected_country}, but {self.country_code} was specified.'
                })
            
        except NumberParseException as e:
            error_messages = {
                NumberParseException.INVALID_COUNTRY_CODE: 'Invalid country code',
                NumberParseException.NOT_A_NUMBER: 'Not a valid phone number',
                NumberParseException.TOO_SHORT_NSN: 'Phone number too short',
                NumberParseException.TOO_LONG: 'Phone number too long',
            }
            
            error_msg = error_messages.get(
                e.error_type,
                f'Cannot parse phone number: {str(e)}'
            )
            
            raise ValidationError({
                'number': f'{error_msg}. Please use international format (e.g., +1234567890) or specify country code.'
            })
    
    def save(self, *args, **kwargs):
        # Валидация перед сохранением
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def formatted_national(self):
        """Format as national number"""
        try:
            parsed = phonenumbers.parse(self.normalized_number)
            return phonenumbers.format_number(
                parsed,
                phonenumbers.PhoneNumberFormat.NATIONAL
            )
        except:
            return self.number
    
    @property
    def formatted_international(self):
        """Format as international number"""
        try:
            parsed = phonenumbers.parse(self.normalized_number)
            return phonenumbers.format_number(
                parsed,
                phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
        except:
            return self.number
    
    @property
    def formatted_e164(self):
        """Format as E.164"""
        return self.normalized_number
    
    @property
    def formatted_rfc3966(self):
        """Format as RFC3966 (tel: URI)"""
        try:
            parsed = phonenumbers.parse(self.normalized_number)
            return phonenumbers.format_number(
                parsed,
                phonenumbers.PhoneNumberFormat.RFC3966
            )
        except:
            return f"tel:{self.number}"
    
    @property
    def click_to_call_url(self):
        """Generate click-to-call URL"""
        return self.formatted_rfc3966
    
    @property
    def carrier_name(self):
        """Get carrier name (if available)"""
        try:
            from phonenumbers import carrier
            parsed = phonenumbers.parse(self.normalized_number)
            name = carrier.name_for_number(parsed, 'en')
            return name if name else 'Unknown'
        except:
            return 'Unknown'
    
    @property
    def number_type_description(self):
        """Get number type description"""
        try:
            parsed = phonenumbers.parse(self.normalized_number)
            number_type = phonenumbers.number_type(parsed)
            
            type_map = {
                phonenumbers.PhoneNumberType.FIXED_LINE: 'Fixed Line',
                phonenumbers.PhoneNumberType.MOBILE: 'Mobile',
                phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: 'Fixed Line or Mobile',
                phonenumbers.PhoneNumberType.TOLL_FREE: 'Toll Free',
                phonenumbers.PhoneNumberType.PREMIUM_RATE: 'Premium Rate',
                phonenumbers.PhoneNumberType.SHARED_COST: 'Shared Cost',
                phonenumbers.PhoneNumberType.VOIP: 'VoIP',
                phonenumbers.PhoneNumberType.PERSONAL_NUMBER: 'Personal Number',
                phonenumbers.PhoneNumberType.PAGER: 'Pager',
                phonenumbers.PhoneNumberType.UAN: 'UAN',
                phonenumbers.PhoneNumberType.VOICEMAIL: 'Voicemail',
            }
            
            return type_map.get(number_type, 'Unknown')
        except:
            return 'Unknown'
    
    @property
    def timezone(self):
        """Get timezone for the number"""
        try:
            from phonenumbers import timezone as tz
            parsed = phonenumbers.parse(self.normalized_number)
            timezones = tz.time_zones_for_number(parsed)
            return ', '.join(timezones) if timezones else 'Unknown'
        except:
            return 'Unknown'
    
    @property
    def geocoding_description(self):
        """Get geographic description"""
        try:
            from phonenumbers import geocoder
            parsed = phonenumbers.parse(self.normalized_number)
            description = geocoder.description_for_number(parsed, 'en')
            return description if description else 'Unknown'
        except:
            return 'Unknown'
    
    @property
    def assigned_to(self):
        """Get assigned object"""
        if self.contact:
            return f"Contact: {self.contact}"
        elif self.device:
            return f"Device: {self.device}"
        elif self.virtual_machine:
            return f"VM: {self.virtual_machine}"
        return "Unassigned"