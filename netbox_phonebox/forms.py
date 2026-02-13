from django import forms
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import (
    DynamicModelChoiceField, 
    DynamicModelMultipleChoiceField, 
    TagFilterField
)
from dcim.models import Device
from virtualization.models import VirtualMachine
from tenancy.models import Contact

from .models import (
    PhoneNumber, TelephonyProvider, PBXServer, 
    SIPTrunk, Extension, CallLog, SECRETS_AVAILABLE
)

if SECRETS_AVAILABLE:
    from netbox_secrets.models import Secret, SecretRole


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
        fields = ['name', 'description', 'website', 'support_phone', 'support_email', 'comments', 'tags']


class PBXServerForm(NetBoxModelForm):
    """Form for PBXServer model"""
    
    # Поле для ввода пароля (не сохраняется напрямую в модель)
    ami_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter AMI password',
            'autocomplete': 'new-password'
        }),
        label='AMI Password',
        help_text='Password will be securely stored in NetBox Secrets'
    )
    
    class Meta:
        model = PBXServer
        fields = [
            'name', 'type', 'hostname', 'ami_port', 'ami_username',
            'web_url', 'enabled', 'description', 'comments', 'tags'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # При редактировании показываем что пароль уже сохранен
        if self.instance.pk:
            if SECRETS_AVAILABLE and hasattr(self.instance, 'ami_secret_ref') and self.instance.ami_secret_ref:
                self.fields['ami_password'].help_text = f'Current: Stored in Secret "{self.instance.ami_secret_ref.name}". Leave empty to keep current password.'
                self.fields['ami_password'].required = False
            elif self.instance.ami_secret:
                self.fields['ami_password'].help_text = 'Current: Stored in legacy field. Enter new password to migrate to Secrets.'
                self.fields['ami_password'].required = False
        else:
            # При создании нового - пароль обязателен
            self.fields['ami_password'].required = True
    
    def clean_ami_password(self):
        """Validate ami_password field"""
        ami_password = self.cleaned_data.get('ami_password')
        
        # При создании нового объекта требуем пароль
        if not self.instance.pk and not ami_password:
            raise forms.ValidationError('AMI Password is required')
        
        return ami_password
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Получаем пароль из cleaned_data (уже проверенные данные)
        ami_password = self.cleaned_data.get('ami_password', '')
        
        # Если введен новый пароль и доступен Secrets
        if ami_password and SECRETS_AVAILABLE:
            try:
                # Получаем или создаем SecretRole для PhoneBox
                role, _ = SecretRole.objects.get_or_create(
                    name='phonebox',
                    defaults={
                        'description': 'PhoneBox secrets (PBX, SIP, Extensions)'
                    }
                )
                
                # Если уже есть Secret - обновляем его
                if hasattr(instance, 'ami_secret_ref') and instance.ami_secret_ref:
                    secret = instance.ami_secret_ref
                    secret.plaintext = ami_password
                    secret.save()
                else:
                    # Создаем новый Secret
                    secret_name = f"{instance.name} AMI Password"
                    secret = Secret.objects.create(
                        role=role,
                        name=secret_name,
                        plaintext=ami_password
                    )
                    instance.ami_secret_ref = secret
                
                # Очищаем legacy поле
                instance.ami_secret = ''
            except Exception as e:
                # Если не удалось создать Secret, сохраняем в legacy поле
                instance.ami_secret = ami_password
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance

class SIPTrunkForm(NetBoxModelForm):
    """Form for SIPTrunk model"""
    
    pbx_server = DynamicModelChoiceField(
        queryset=PBXServer.objects.all()
    )
    
    provider = DynamicModelChoiceField(
        queryset=TelephonyProvider.objects.all(),
        required=False
    )
    
    # Поле для ввода пароля
    sip_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter SIP password (optional)',
            'autocomplete': 'new-password'
        }),
        label='SIP Password',
        help_text='Password will be securely stored in NetBox Secrets'
    )
    
    class Meta:
        model = SIPTrunk
        fields = [
            'name', 'pbx_server', 'provider', 'type', 'host', 'port',
            'transport', 'username', 'context',
            'enabled', 'description', 'comments', 'tags'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # При редактировании показываем что пароль уже сохранен
        if self.instance.pk:
            if SECRETS_AVAILABLE and hasattr(self.instance, 'secret_ref') and self.instance.secret_ref:
                self.fields['sip_password'].help_text = f'Current: Stored in Secret "{self.instance.secret_ref.name}". Leave empty to keep current password.'
            elif self.instance.secret:
                self.fields['sip_password'].help_text = 'Current: Stored in legacy field. Enter new password to migrate to Secrets.'
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        sip_password = cleaned_data.get('sip_password')
        
        # Если указан username, рекомендуем пароль (но не требуем)
        if username and not sip_password and not self.instance.pk:
            # Только предупреждение, не ошибка
            pass
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Получаем пароль из cleaned_data
        sip_password = self.cleaned_data.get('sip_password', '')
        
        # Если введен новый пароль и доступен Secrets
        if sip_password and SECRETS_AVAILABLE:
            try:
                role, _ = SecretRole.objects.get_or_create(
                    name='phonebox',
                    defaults={
                        'description': 'PhoneBox secrets (PBX, SIP, Extensions)'
                    }
                )
                
                # Если уже есть Secret - обновляем его
                if hasattr(instance, 'secret_ref') and instance.secret_ref:
                    secret = instance.secret_ref
                    secret.plaintext = sip_password
                    secret.save()
                else:
                    # Создаем новый Secret
                    secret_name = f"{instance.name} SIP Password"
                    secret = Secret.objects.create(
                        role=role,
                        name=secret_name,
                        plaintext=sip_password
                    )
                    instance.secret_ref = secret
                
                # Очищаем legacy поле
                instance.secret = ''
            except Exception as e:
                # Если не удалось создать Secret, сохраняем в legacy поле
                instance.secret = sip_password
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance

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
    
    # Поле для ввода пароля
    extension_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter extension password (optional)',
            'autocomplete': 'new-password'
        }),
        label='Extension Password',
        help_text='Password will be securely stored in NetBox Secrets'
    )
    
    class Meta:
        model = Extension
        fields = [
            'extension', 'pbx_server', 'type', 'contact', 'device',
            'enabled', 'description', 'comments', 'tags'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # При редактировании показываем что пароль уже сохранен
        if self.instance.pk:
            if SECRETS_AVAILABLE and hasattr(self.instance, 'secret_ref') and self.instance.secret_ref:
                self.fields['extension_password'].help_text = f'Current: Stored in Secret "{self.instance.secret_ref.name}". Leave empty to keep current password.'
            elif self.instance.secret:
                self.fields['extension_password'].help_text = 'Current: Stored in legacy field. Enter new password to migrate to Secrets.'
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Получаем пароль из cleaned_data
        extension_password = self.cleaned_data.get('extension_password', '')
        
        # Если введен новый пароль и доступен Secrets
        if extension_password and SECRETS_AVAILABLE:
            try:
                role, _ = SecretRole.objects.get_or_create(
                    name='phonebox',
                    defaults={
                        'description': 'PhoneBox secrets (PBX, SIP, Extensions)'
                    }
                )
                
                # Если уже есть Secret - обновляем его
                if hasattr(instance, 'secret_ref') and instance.secret_ref:
                    secret = instance.secret_ref
                    secret.plaintext = extension_password
                    secret.save()
                else:
                    # Создаем новый Secret
                    secret_name = f"Extension {instance.extension} Password"
                    secret = Secret.objects.create(
                        role=role,
                        name=secret_name,
                        plaintext=extension_password
                    )
                    instance.secret_ref = secret
                
                # Очищаем legacy поле
                instance.secret = ''
            except Exception as e:
                # Если не удалось создать Secret, сохраняем в legacy поле
                instance.secret = extension_password
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance

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


# FilterSet Forms (без изменений)

class PhoneNumberFilterForm(NetBoxModelFilterSetForm):
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
    model = TelephonyProvider
    tag = TagFilterField(model)


class PBXServerFilterForm(NetBoxModelFilterSetForm):
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