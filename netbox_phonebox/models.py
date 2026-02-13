from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from netbox.models import NetBoxModel
from dcim.models import Device
from virtualization.models import VirtualMachine
from tenancy.models import Contact
import phonenumbers
from phonenumbers import NumberParseException
from utilities.choices import ChoiceSet

# Импорт для интеграции с netbox-secrets
try:
    from netbox_secrets.models import Secret, SecretRole
    SECRETS_AVAILABLE = True
except ImportError:
    SECRETS_AVAILABLE = False

class TelephonyProvider(NetBoxModel):
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
        verbose_name = 'Telephony Provider'
        verbose_name_plural = 'Telephony Providers'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('plugins:netbox_phonebox:telephonyprovider', args=[self.pk])
    
    @property
    def numbers_count(self):
        """Count of phone numbers"""
        return self.phone_numbers.count()
    
    @property
    def active_numbers_count(self):
        """Count of active phone numbers"""
        return self.phone_numbers.filter(status='active').count()
    
    @property
    def reserved_numbers_count(self):
        """Count of reserved phone numbers"""
        return self.phone_numbers.filter(status='reserved').count()
    
    @property
    def deprecated_numbers_count(self):
        """Count of deprecated phone numbers"""
        return self.phone_numbers.filter(status='deprecated').count()


class PBXServer(NetBoxModel):
    """PBX Server (Asterisk/FreePBX/Grandstream UCM)"""
    
    TYPE_CHOICES = [
        ('asterisk', 'Asterisk'),
        ('freepbx', 'FreePBX'),
        ('grandstream_ucm', 'Grandstream UCM'),
        ('3cx', '3CX'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text='PBX server name'
    )
    
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='asterisk',
        help_text='PBX type'
    )
    
    hostname = models.CharField(
        max_length=255,
        help_text='PBX hostname or IP address'
    )
    
    ami_port = models.PositiveIntegerField(
        default=5038,
        help_text='AMI port (default: 5038)'
    )
    
    ami_username = models.CharField(
        max_length=100,
        help_text='AMI username'
    )
    
    # Опция 1: Прямое хранение (legacy, для обратной совместимости)
    ami_secret = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='AMI secret/password (deprecated - use ami_secret_ref instead)'
    )
    
    # Опция 2: Ссылка на Secret (рекомендуется)
    if SECRETS_AVAILABLE:
        ami_secret_ref = models.ForeignKey(
            to='netbox_secrets.Secret',
            on_delete=models.SET_NULL,
            blank=True,
            null=True,
            related_name='pbx_servers',
            help_text='AMI secret from NetBox Secrets'
        )
    
    web_url = models.URLField(
        blank=True,
        help_text='PBX web interface URL'
    )
    
    enabled = models.BooleanField(
        default=True,
        help_text='Enable this PBX server'
    )
    
    description = models.CharField(
        max_length=200,
        blank=True
    )
    
    comments = models.TextField(
        blank=True
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = 'PBX Server'
        verbose_name_plural = 'PBX Servers'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('plugins:netbox_phonebox:pbxserver', args=[self.pk])
    
    @property
    def connection_string(self):
        """Get AMI connection string"""
        return f"{self.ami_username}@{self.hostname}:{self.ami_port}"
    
    def get_ami_secret(self):
        """
        Get AMI secret from Secret reference or direct field
        
        Returns:
            str: AMI secret/password
        """
        if SECRETS_AVAILABLE and hasattr(self, 'ami_secret_ref') and self.ami_secret_ref:
            try:
                return self.ami_secret_ref.plaintext
            except Exception as e:
                # Fallback to direct field if secret decryption fails
                return self.ami_secret
        return self.ami_secret


class SIPTrunk(NetBoxModel):
    """SIP Trunk configuration"""
    
    TYPE_CHOICES = [
        ('peer', 'Peer'),
        ('user', 'User'),
        ('friend', 'Friend'),
    ]
    
    TRANSPORT_CHOICES = [
        ('udp', 'UDP'),
        ('tcp', 'TCP'),
        ('tls', 'TLS'),
        ('ws', 'WebSocket'),
        ('wss', 'WebSocket Secure'),
    ]
    
    name = models.CharField(
        max_length=100,
        help_text='SIP trunk name'
    )
    
    pbx_server = models.ForeignKey(
        to='PBXServer',
        on_delete=models.CASCADE,
        related_name='sip_trunks',
        help_text='PBX server'
    )
    
    provider = models.ForeignKey(
        to='TelephonyProvider',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='sip_trunks',
        help_text='Telephony provider'
    )
    
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default='peer',
        help_text='SIP trunk type'
    )
    
    host = models.CharField(
        max_length=255,
        help_text='SIP host/IP'
    )
    
    port = models.PositiveIntegerField(
        default=5060,
        help_text='SIP port'
    )
    
    transport = models.CharField(
        max_length=10,
        choices=TRANSPORT_CHOICES,
        default='udp',
        help_text='Transport protocol'
    )
    
    username = models.CharField(
        max_length=100,
        blank=True,
        help_text='SIP username'
    )
    
    # Опция 1: Прямое хранение (legacy)
    secret = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='SIP secret/password (deprecated - use secret_ref instead)'
    )
    
    # Опция 2: Ссылка на Secret (рекомендуется)
    if SECRETS_AVAILABLE:
        secret_ref = models.ForeignKey(
            to='netbox_secrets.Secret',
            on_delete=models.SET_NULL,
            blank=True,
            null=True,
            related_name='sip_trunks',
            help_text='SIP secret from NetBox Secrets'
        )
    
    context = models.CharField(
        max_length=100,
        default='from-trunk',
        help_text='Dialplan context'
    )
    
    enabled = models.BooleanField(
        default=True,
        help_text='Enable this trunk'
    )
    
    description = models.CharField(
        max_length=200,
        blank=True
    )
    
    comments = models.TextField(
        blank=True
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = 'SIP Trunk'
        verbose_name_plural = 'SIP Trunks'
        unique_together = ['pbx_server', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.pbx_server})"
    
    def get_absolute_url(self):
        return reverse('plugins:netbox_phonebox:siptrunk', args=[self.pk])
    
    def get_secret(self):
        """
        Get SIP secret from Secret reference or direct field
        
        Returns:
            str: SIP secret/password
        """
        if SECRETS_AVAILABLE and hasattr(self, 'secret_ref') and self.secret_ref:
            try:
                return self.secret_ref.plaintext
            except Exception as e:
                return self.secret
        return self.secret


class Extension(NetBoxModel):
    """Extension configuration"""
    
    TYPE_CHOICES = [
        ('pjsip', 'PJSIP'),
        ('sip', 'SIP'),
        ('iax2', 'IAX2'),
    ]
    
    extension = models.CharField(
        max_length=20,
        help_text='Extension number'
    )
    
    pbx_server = models.ForeignKey(
        to='PBXServer',
        on_delete=models.CASCADE,
        related_name='extensions',
        help_text='PBX server'
    )
    
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default='pjsip',
        help_text='Extension type'
    )
    
    contact = models.ForeignKey(
        to=Contact,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='extensions',
        help_text='Assigned contact'
    )
    
    device = models.ForeignKey(
        to=Device,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='extensions',
        help_text='Assigned device (IP phone)'
    )
    
    # Опция 1: Прямое хранение (legacy)
    secret = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='Extension secret/password (deprecated - use secret_ref instead)'
    )
    
    # Опция 2: Ссылка на Secret (рекомендуется)
    if SECRETS_AVAILABLE:
        secret_ref = models.ForeignKey(
            to='netbox_secrets.Secret',
            on_delete=models.SET_NULL,
            blank=True,
            null=True,
            related_name='extensions',
            help_text='Extension secret from NetBox Secrets'
        )
    
    enabled = models.BooleanField(
        default=True,
        help_text='Enable this extension'
    )
    
    description = models.CharField(
        max_length=200,
        blank=True
    )
    
    comments = models.TextField(
        blank=True
    )
    
    class Meta:
        ordering = ['extension']
        verbose_name = 'Extension'
        verbose_name_plural = 'Extensions'
        unique_together = ['pbx_server', 'extension']
    
    def __str__(self):
        return f"{self.extension} ({self.pbx_server})"
    
    def get_absolute_url(self):
        return reverse('plugins:netbox_phonebox:extension', args=[self.pk])
    
    def get_secret(self):
        """
        Get extension secret from Secret reference or direct field
        
        Returns:
            str: Extension secret/password
        """
        if SECRETS_AVAILABLE and hasattr(self, 'secret_ref') and self.secret_ref:
            try:
                return self.secret_ref.plaintext
            except Exception as e:
                return self.secret
        return self.secret


class CallLog(NetBoxModel):
    """Call history log"""
    
    DIRECTION_CHOICES = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
        ('internal', 'Internal'),
    ]
    
    STATUS_CHOICES = [
        ('answered', 'Answered'),
        ('no_answer', 'No Answer'),
        ('busy', 'Busy'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    call_id = models.CharField(
        max_length=255,
        unique=True,
        help_text='Unique call ID from PBX'
    )
    
    pbx_server = models.ForeignKey(
        PBXServer,
        on_delete=models.CASCADE,
        related_name='call_logs',
        help_text='PBX server'
    )
    
    direction = models.CharField(
        max_length=20,
        choices=DIRECTION_CHOICES,
        help_text='Call direction'
    )
    
    caller_number = models.CharField(
        max_length=50,
        help_text='Caller phone number'
    )
    
    called_number = models.CharField(
        max_length=50,
        help_text='Called phone number'
    )
    
    extension = models.ForeignKey(
        Extension,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='call_logs',
        help_text='Extension involved'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        help_text='Call status'
    )
    
    start_time = models.DateTimeField(
        help_text='Call start time'
    )
    
    answer_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Call answer time'
    )
    
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Call end time'
    )
    
    duration = models.IntegerField(
        default=0,
        help_text='Call duration in seconds'
    )
    
    recording_url = models.URLField(
        blank=True,
        help_text='Call recording URL'
    )
    
    comments = models.TextField(
        blank=True
    )
    
    class Meta:
        ordering = ['-start_time']
        verbose_name = 'Call Log'
        verbose_name_plural = 'Call Logs'
        indexes = [
            models.Index(fields=['-start_time']),
            models.Index(fields=['caller_number']),
            models.Index(fields=['called_number']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.caller_number} → {self.called_number} ({self.start_time})"
    
    def get_absolute_url(self):
        return reverse('plugins:netbox_phonebox:calllog', args=[self.pk])
    
    @property
    def duration_formatted(self):
        """Format duration as HH:MM:SS"""
        hours = self.duration // 3600
        minutes = (self.duration % 3600) // 60
        seconds = self.duration % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


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
        TelephonyProvider,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='phone_numbers',
        help_text='Service provider'
    )
    
    extension = models.ForeignKey(
        Extension,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='phone_numbers',
        help_text='Associated extension'
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
        verbose_name = 'Phone Number'
        verbose_name_plural = 'Phone Numbers'
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
            region = self.country_code if self.country_code else None
            parsed = phonenumbers.parse(self.number, region)
            
            if not phonenumbers.is_valid_number(parsed):
                raise ValidationError({
                    'number': f'Invalid phone number format. Please use international format (e.g., +1234567890)'
                })
            
            self.normalized_number = phonenumbers.format_number(
                parsed,
                phonenumbers.PhoneNumberFormat.E164
            )
            
            detected_country = phonenumbers.region_code_for_number(parsed)
            
            if not self.country_code:
                self.country_code = detected_country
            elif self.country_code != detected_country:
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
        if self.extension and self.extension.pbx_server:
            # Генерируем URL для звонка через PBX
            return reverse('plugins:netbox_phonebox:make_call') + f'?number={self.normalized_number}&extension={self.extension.extension}'
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
    
    @property
    def call_count(self):
        """Get total call count"""
        from django.db.models import Q
        return CallLog.objects.filter(
            Q(caller_number=self.normalized_number) | Q(called_number=self.normalized_number)
        ).count()
    
    @property
    def last_call(self):
        """Get last call"""
        from django.db.models import Q
        return CallLog.objects.filter(
            Q(caller_number=self.normalized_number) | Q(called_number=self.normalized_number)
        ).order_by('-start_time').first()