from django import forms
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import (
    DynamicModelChoiceField, 
    DynamicModelMultipleChoiceField, 
    TagFilterField
)
from dcim.models import Device, Site, Location
from virtualization.models import VirtualMachine
from tenancy.models import Contact

from .models import (
    PhoneNumber, TelephonyProvider, PBXServer, 
    SIPTrunk, Extension, CallLog, SECRETS_AVAILABLE
)

# Импорт Secret если доступен
if SECRETS_AVAILABLE:
    from netbox_secrets.models import Secret


class PhoneNumberForm(NetBoxModelForm):
    """Form for PhoneNumber model"""
    
    contact = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        required=False
    )
    
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    
    virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False
    )
    
    provider = DynamicModelChoiceField(
        queryset=TelephonyProvider.objects.all(),
        required=False
    )
    
    extension = DynamicModelChoiceField(
        queryset=Extension.objects.all(),
        required=False,
        query_params={
            'pbx_server_id': '$pbx_server'
        }
    )
    
    class Meta:
        model = PhoneNumber
        fields = [
            'number', 'type', 'status', 'contact', 'device', 'virtual_machine',
            'provider', 'extension', 'description', 'comments', 'tags'
        ]


class TelephonyProviderForm(NetBoxModelForm):
    """Form for TelephonyProvider model"""
    
    class Meta:
        model = TelephonyProvider
        fields = [
            'name', 'description', 'website', 'support_phone', 
            'support_email', 'comments', 'tags'
        ]


class PBXServerForm(NetBoxModelForm):
    """Form for PBXServer model"""
    
    class Meta:
        model = PBXServer
        fields = [
            'name', 'type', 'hostname', 'ami_port', 'ami_username',
            'ami_secret', 'web_url', 'enabled', 'description',
            'comments', 'tags'
        ]
        
        widgets = {
            'ami_secret': forms.PasswordInput(
                attrs={
                    'placeholder': 'Enter AMI password (or use Secret reference)',
                    'autocomplete': 'new-password'
                }
            ),
        }
        
        help_texts = {
            'ami_secret': 'AMI password (legacy method - consider using Secret reference instead)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Динамически добавляем ami_secret_ref в fields если доступен
        if SECRETS_AVAILABLE:
            self.fields['ami_secret_ref'] = DynamicModelChoiceField(
                queryset=Secret.objects.all(),
                required=False,
                label='AMI Secret (from Secrets)',
                help_text='Select secret from NetBox Secrets (recommended)'
            )
            
            # Переупорядочиваем поля
            field_order = list(self.fields.keys())
            if 'ami_secret' in field_order:
                ami_secret_index = field_order.index('ami_secret')
                field_order.insert(ami_secret_index + 1, 'ami_secret_ref')
                self.order_fields(field_order)
    
    def clean(self):
        cleaned_data = super().clean()
        ami_secret = cleaned_data.get('ami_secret')
        ami_secret_ref = cleaned_data.get('ami_secret_ref') if SECRETS_AVAILABLE else None
        
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
    
    class Meta:
        model = SIPTrunk
        fields = [
            'name', 'pbx_server', 'provider', 'type', 'host', 'port',
            'transport', 'username', 'secret', 'context',
            'enabled', 'description', 'comments', 'tags'
        ]
        
        widgets = {
            'secret': forms.PasswordInput(
                attrs={
                    'placeholder': 'Enter SIP password (or use Secret reference)',
                    'autocomplete': 'new-password'
                }
            ),
        }
        
        help_texts = {
            'secret': 'SIP password (legacy method - consider using Secret reference instead)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Динамически добавляем secret_ref в fields если доступен
        if SECRETS_AVAILABLE:
            self.fields['secret_ref'] = DynamicModelChoiceField(
                queryset=Secret.objects.all(),
                required=False,
                label='Secret (from Secrets)',
                help_text='Select secret from NetBox Secrets (recommended)'
            )
            
            # Переупорядочиваем поля
            field_order = list(self.fields.keys())
            if 'secret' in field_order:
                secret_index = field_order.index('secret')
                field_order.insert(secret_index + 1, 'secret_ref')
                self.order_fields(field_order)
    
    def clean(self):
        cleaned_data = super().clean()
        secret = cleaned_data.get('secret')
        secret_ref = cleaned_data.get('secret_ref') if SECRETS_AVAILABLE else None
        
        # Хотя бы один метод должен быть указан (если указан username)
        username = cleaned_data.get('username')
        if username and not secret and not secret_ref:
            raise forms.ValidationError(
                'Please provide either Secret or Secret Reference when Username is specified'
            )
        
        return cleaned_data


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
    
    class Meta:
        model = Extension
        fields = [
            'extension', 'pbx_server', 'type', 'contact', 'device',
            'secret', 'enabled', 'description', 'comments', 'tags'
        ]
        
        widgets = {
            'secret': forms.PasswordInput(
                attrs={
                    'placeholder': 'Enter extension password (or use Secret reference)',
                    'autocomplete': 'new-password'
                }
            ),
        }
        
        help_texts = {
            'secret': 'Extension password (legacy method - consider using Secret reference instead)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Динамически добавляем secret_ref в fields если доступен
        if SECRETS_AVAILABLE:
            self.fields['secret_ref'] = DynamicModelChoiceField(
                queryset=Secret.objects.all(),
                required=False,
                label='Secret (from Secrets)',
                help_text='Select secret from NetBox Secrets (recommended)'
            )
            
            # Переупорядочиваем поля
            field_order = list(self.fields.keys())
            if 'secret' in field_order:
                secret_index = field_order.index('secret')
                field_order.insert(secret_index + 1, 'secret_ref')
                self.order_fields(field_order)


class MakeCallForm(forms.Form):
    """Form for initiating a call"""
    
    pbx_server = DynamicModelChoiceField(
        queryset=PBXServer.objects.filter(enabled=True),
        required=True,
        label='PBX Server',
        help_text='Select PBX server to use'
    )
    
    from_extension = DynamicModelChoiceField(
        queryset=Extension.objects.filter(enabled=True),
        required=True,
        label='From Extension',
        help_text='Extension to call from',
        query_params={
            'pbx_server_id': '$pbx_server'
        }
    )
    
    to_number = forms.CharField(
        max_length=50,
        required=True,
        label='To Number',
        help_text='Number to call (e.g., +79991234567 or extension)',
        widget=forms.TextInput(attrs={
            'placeholder': '+79991234567'
        })
    )
    
    caller_id = forms.CharField(
        max_length=50,
        required=False,
        label='Caller ID',
        help_text='Optional caller ID to display',
        widget=forms.TextInput(attrs={
            'placeholder': 'Optional'
        })
    )


# FilterSet Forms

class PhoneNumberFilterForm(NetBoxModelFilterSetForm):
    """Filter form for PhoneNumber model"""
    
    model = PhoneNumber
    
    type = forms.MultipleChoiceField(
        choices=PhoneNumber.TYPE_CHOICES,
        required=False
    )
    
    status = forms.MultipleChoiceField(
        choices=PhoneNumber.STATUS_CHOICES,
        required=False
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
    
    provider_id = DynamicModelMultipleChoiceField(
        queryset=TelephonyProvider.objects.all(),
        required=False,
        label='Provider'
    )
    
    extension_id = DynamicModelMultipleChoiceField(
        queryset=Extension.objects.all(),
        required=False,
        label='Extension'
    )
    
    tag = TagFilterField(model)


class TelephonyProviderFilterForm(NetBoxModelFilterSetForm):
    """Filter form for TelephonyProvider model"""
    
    model = TelephonyProvider
    tag = TagFilterField(model)


class PBXServerFilterForm(NetBoxModelFilterSetForm):
    """Filter form for PBXServer model"""
    
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


class SIPTrunkFilterForm(NetBoxModelFilterSetForm):
    """Filter form for SIPTrunk model"""
    
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
    
    transport = forms.MultipleChoiceField(
        choices=SIPTrunk.TRANSPORT_CHOICES,
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


class ExtensionFilterForm(NetBoxModelFilterSetForm):
    """Filter form for Extension model"""
    
    model = Extension
    
    pbx_server_id = DynamicModelMultipleChoiceField(
        queryset=PBXServer.objects.all(),
        required=False,
        label='PBX Server'
    )
    
    type = forms.MultipleChoiceField(
        choices=Extension.TYPE_CHOICES,
        required=False
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
    """Filter form for CallLog model"""
    
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
    
    tag = TagFilterField(model)