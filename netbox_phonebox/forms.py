from django import forms
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from dcim.models import Device
from virtualization.models import VirtualMachine
from tenancy.models import Contact
from utilities.forms.fields import DynamicModelChoiceField, DynamicModelMultipleChoiceField, TagFilterField
from .models import PhoneNumber, TelephonyProvider  # Изменено
from .models import (
    PhoneNumber, TelephonyProvider, PBXServer, 
    SIPTrunk, Extension, CallLog
)

class PhoneNumberForm(NetBoxModelForm):
    """Form for creating/editing phone numbers"""
    
    provider = DynamicModelChoiceField(
        queryset=TelephonyProvider.objects.all(),  # Изменено
        required=False
    )
    
    contact = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        required=False
    )
    
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False
    )
    
    virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False
    )
    
    class Meta:
        model = PhoneNumber
        fields = [
            'number', 'country_code', 'type', 'status', 'provider',
            'contact', 'device', 'virtual_machine', 'description',
            'comments', 'tags'
        ]
        help_texts = {
            'number': 'Enter phone number in international format (e.g., +1234567890) or specify country code',
            'country_code': 'Optional. Will be auto-detected if not provided (e.g., RU, US, GB)',
        }


class PhoneNumberFilterForm(NetBoxModelFilterSetForm):
    """Filter form for phone numbers"""
    
    model = PhoneNumber
    
    type = forms.MultipleChoiceField(
        choices=PhoneNumber.TYPE_CHOICES,
        required=False
    )
    
    status = forms.MultipleChoiceField(
        choices=PhoneNumber.STATUS_CHOICES,
        required=False
    )
    
    provider_id = DynamicModelMultipleChoiceField(
        queryset=TelephonyProvider.objects.all(),  # Изменено
        required=False,
        label='Provider'
    )
    
    contact_id = DynamicModelMultipleChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        label='Contact'
    )
    
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label='Device'
    )
    
    virtual_machine_id = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label='Virtual Machine'
    )
    
    tag = TagFilterField(model)


class TelephonyProviderForm(NetBoxModelForm):  # Изменено
    """Form for creating/editing telephony providers"""
    
    class Meta:
        model = TelephonyProvider  # Изменено
        fields = [
            'name', 'description', 'website', 'support_phone',
            'support_email', 'comments', 'tags'
        ]


class TelephonyProviderFilterForm(NetBoxModelFilterSetForm):  # Изменено
    """Filter form for telephony providers"""
    
    model = TelephonyProvider  # Изменено
    tag = TagFilterField(model)


class PhoneNumberImportForm(forms.Form):
    """Form for importing phone numbers from CSV"""
    
    csv_file = forms.FileField(
        label='CSV File',
        help_text='Upload CSV file with columns: number, type, status, country_code, provider, description'
    )
    
    update_existing = forms.BooleanField(
        required=False,
        initial=False,
        label='Update existing numbers',
        help_text='Update existing phone numbers if they already exist (matched by normalized number)'
    )


class PhoneNumberBulkImportForm(forms.Form):
    """Form for bulk import with text area"""
    
    numbers = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10}),
        label='Phone Numbers',
        help_text='Enter one phone number per line. Format: +1234567890 or specify country code in form'
    )
    
    country_code = forms.CharField(
        max_length=5,
        required=False,
        label='Default Country Code',
        help_text='Default country code for numbers without country prefix (e.g., RU, US)'
    )
    
    type = forms.ChoiceField(
        choices=PhoneNumber.TYPE_CHOICES,
        initial='mobile',
        label='Type'
    )
    
    status = forms.ChoiceField(
        choices=PhoneNumber.STATUS_CHOICES,
        initial='active',
        label='Status'
    )
    
    provider = DynamicModelChoiceField(
        queryset=TelephonyProvider.objects.all(),  # Изменено
        required=False,
        label='Provider'
    )
    
class PBXServerForm(NetBoxModelForm):
    """Form for creating/editing PBX servers"""
    
    class Meta:
        model = PBXServer
        fields = [
            'name', 'type', 'hostname', 'ami_port', 'ami_username',
            'ami_secret', 'web_url', 'enabled', 'description',
            'comments', 'tags'
        ]
        widgets = {
            'ami_secret': forms.PasswordInput(render_value=True),
        }


class PBXServerFilterForm(NetBoxModelFilterSetForm):
    """Filter form for PBX servers"""
    
    model = PBXServer
    
    type = forms.MultipleChoiceField(
        choices=PBXServer.TYPE_CHOICES,
        required=False
    )
    
    enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=[
            ('', '---------'),
            ('true', 'Yes'),
            ('false', 'No'),
        ])
    )
    
    tag = TagFilterField(model)


class PBXServerForm(NetBoxModelForm):
    """Form for PBXServer model"""
    
    if SECRETS_AVAILABLE:
        ami_secret_ref = DynamicModelChoiceField(
            queryset=Secret.objects.all(),
            required=False,
            label='AMI Secret (from Secrets)',
            help_text='Select secret from NetBox Secrets (recommended)'
        )
    
    class Meta:
        model = PBXServer
        fields = [
            'name', 'type', 'hostname', 'ami_port', 'ami_username',
            'ami_secret', 'web_url', 'enabled', 'description',
            'comments', 'tags'
        ]
        
        # Добавляем ami_secret_ref если доступен
        if SECRETS_AVAILABLE:
            fields.insert(fields.index('ami_secret') + 1, 'ami_secret_ref')
        
        widgets = {
            'ami_secret': forms.PasswordInput(
                attrs={'placeholder': 'Enter AMI password (or use Secret reference)'}
            ),
        }
        
        help_texts = {
            'ami_secret': 'AMI password (legacy method - consider using Secret reference instead)',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        ami_secret = cleaned_data.get('ami_secret')
        ami_secret_ref = cleaned_data.get('ami_secret_ref')
        
        # Требуем хотя бы один из методов
        if not ami_secret and not ami_secret_ref:
            raise forms.ValidationError(
                'Please provide either AMI Secret or AMI Secret Reference'
            )
        
        return cleaned_data


class SIPTrunkForm(NetBoxModelForm):
    """Form for SIPTrunk model"""
    
    pbx_server = DynamicModelChoiceField(
        queryset=PBXServer.objects.all()
    )
    
    provider = DynamicModelChoiceField(
        queryset=TelephonyProvider.objects.all(),
        required=False
    )
    
    if SECRETS_AVAILABLE:
        secret_ref = DynamicModelChoiceField(
            queryset=Secret.objects.all(),
            required=False,
            label='Secret (from Secrets)',
            help_text='Select secret from NetBox Secrets (recommended)'
        )
    
    class Meta:
        model = SIPTrunk
        fields = [
            'name', 'pbx_server', 'provider', 'type', 'host', 'port',
            'transport', 'username', 'secret', 'context',
            'enabled', 'description', 'comments', 'tags'
        ]
        
        if SECRETS_AVAILABLE:
            fields.insert(fields.index('secret') + 1, 'secret_ref')
        
        widgets = {
            'secret': forms.PasswordInput(
                attrs={'placeholder': 'Enter SIP password (or use Secret reference)'}
            ),
        }
        
        help_texts = {
            'secret': 'SIP password (legacy method - consider using Secret reference instead)',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        secret = cleaned_data.get('secret')
        secret_ref = cleaned_data.get('secret_ref')
        
        # Хотя бы один метод должен быть указан
        if not secret and not secret_ref:
            raise forms.ValidationError(
                'Please provide either Secret or Secret Reference'
            )
        
        return cleaned_data

class SIPTrunkFilterForm(NetBoxModelFilterSetForm):
    """Filter form for SIP trunks"""
    
    model = SIPTrunk
    
    pbx_server_id = DynamicModelMultipleChoiceField(
        queryset=PBXServer.objects.all(),
        required=False,
        label='PBX Server'
    )
    
    provider_id = DynamicModelMultipleChoiceField(
        queryset=TelephonyProvider.objects.all(),
        required=False,
        label='Provider'
    )
    
    type = forms.MultipleChoiceField(
        choices=SIPTrunk.TYPE_CHOICES,
        required=False
    )
    
    enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=[
            ('', '---------'),
            ('true', 'Yes'),
            ('false', 'No'),
        ])
    )
    
    tag = TagFilterField(model)


class ExtensionForm(NetBoxModelForm):
    """Form for Extension model"""
    
    pbx_server = DynamicModelChoiceField(
        queryset=PBXServer.objects.all()
    )
    
    contact = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        required=False
    )
    
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False
    )
    
    if SECRETS_AVAILABLE:
        secret_ref = DynamicModelChoiceField(
            queryset=Secret.objects.all(),
            required=False,
            label='Secret (from Secrets)',
            help_text='Select secret from NetBox Secrets (recommended)'
        )
    
    class Meta:
        model = Extension
        fields = [
            'extension', 'pbx_server', 'type', 'contact', 'device',
            'secret', 'enabled', 'description', 'comments', 'tags'
        ]
        
        if SECRETS_AVAILABLE:
            fields.insert(fields.index('secret') + 1, 'secret_ref')
        
        widgets = {
            'secret': forms.PasswordInput(
                attrs={'placeholder': 'Enter extension password (or use Secret reference)'}
            ),
        }
        
        help_texts = {
            'secret': 'Extension password (legacy method - consider using Secret reference instead)',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        secret = cleaned_data.get('secret')
        secret_ref = cleaned_data.get('secret_ref')
        
        # Хотя бы один метод должен быть указан (если указан любой)
        # Можно сделать оба необязательными для некоторых типов extensions
        
        return cleaned_data

class ExtensionFilterForm(NetBoxModelFilterSetForm):
    """Filter form for extensions"""
    
    model = Extension
    
    pbx_server_id = DynamicModelMultipleChoiceField(
        queryset=PBXServer.objects.all(),
        required=False,
        label='PBX Server'
    )
    
    contact_id = DynamicModelMultipleChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        label='Contact'
    )
    
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label='Device'
    )
    
    type = forms.MultipleChoiceField(
        choices=Extension.TYPE_CHOICES,
        required=False
    )
    
    enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=[
            ('', '---------'),
            ('true', 'Yes'),
            ('false', 'No'),
        ])
    )
    
    tag = TagFilterField(model)


class CallLogFilterForm(NetBoxModelFilterSetForm):
    """Filter form for call logs"""
    
    model = CallLog
    
    pbx_server_id = DynamicModelMultipleChoiceField(
        queryset=PBXServer.objects.all(),
        required=False,
        label='PBX Server'
    )
    
    extension_id = DynamicModelMultipleChoiceField(
        queryset=Extension.objects.all(),
        required=False,
        label='Extension'
    )
    
    direction = forms.MultipleChoiceField(
        choices=CallLog.DIRECTION_CHOICES,
        required=False
    )
    
    status = forms.MultipleChoiceField(
        choices=CallLog.STATUS_CHOICES,
        required=False
    )
    
    start_time_after = forms.DateTimeField(
        required=False,
        label='Start Time After',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
    
    start_time_before = forms.DateTimeField(
        required=False,
        label='Start Time Before',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
    
    tag = TagFilterField(model)


class MakeCallForm(forms.Form):
    """Form for initiating a call"""
    
    pbx_server = DynamicModelChoiceField(
        queryset=PBXServer.objects.filter(enabled=True),
        label='PBX Server'
    )
    
    extension = DynamicModelChoiceField(
        queryset=Extension.objects.filter(enabled=True),
        label='From Extension',
        query_params={'pbx_server_id': '$pbx_server'}
    )
    
    to_number = forms.CharField(
        max_length=50,
        label='To Number',
        help_text='Phone number to call (international format recommended)'
    )