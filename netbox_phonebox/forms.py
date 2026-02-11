from django import forms
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from dcim.models import Device
from virtualization.models import VirtualMachine
from tenancy.models import Contact
from utilities.forms.fields import DynamicModelChoiceField, DynamicModelMultipleChoiceField, TagFilterField
from .models import PhoneNumber, TelephonyProvider  # Изменено


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