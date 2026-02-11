import django_filters
from netbox.filtersets import NetBoxModelFilterSet
from dcim.models import Device
from virtualization.models import VirtualMachine
from tenancy.models import Contact
from utilities.filters import MultiValueCharFilter
from .models import (
    PhoneNumber, TelephonyProvider, PBXServer, 
    SIPTrunk, Extension, CallLog
)


class TelephonyProviderFilterSet(NetBoxModelFilterSet):  # Изменено
    """FilterSet for TelephonyProvider model"""
    
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    
    class Meta:
        model = TelephonyProvider  # Изменено
        fields = ['id', 'name', 'website', 'support_phone', 'support_email']
    
    def search(self, queryset, name, value):
        """Search in multiple fields"""
        if not value.strip():
            return queryset
        return queryset.filter(
            django_filters.Q(name__icontains=value) |
            django_filters.Q(description__icontains=value) |
            django_filters.Q(website__icontains=value) |
            django_filters.Q(support_phone__icontains=value) |
            django_filters.Q(support_email__icontains=value)
        )


class PhoneNumberFilterSet(NetBoxModelFilterSet):
    """FilterSet for PhoneNumber model"""
    
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    
    type = django_filters.MultipleChoiceFilter(
        choices=PhoneNumber.TYPE_CHOICES,
        null_value=None
    )
    
    status = django_filters.MultipleChoiceFilter(
        choices=PhoneNumber.STATUS_CHOICES,
        null_value=None
    )
    
    country_code = MultiValueCharFilter()
    
    provider_id = django_filters.ModelMultipleChoiceFilter(
        queryset=TelephonyProvider.objects.all(),  # Изменено
        label='Provider',
    )
    
    contact_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Contact.objects.all(),
        label='Contact',
    )
    
    device_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label='Device',
    )
    
    virtual_machine_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VirtualMachine.objects.all(),
        label='Virtual Machine',
    )
    
    class Meta:
        model = PhoneNumber
        fields = [
            'id', 'number', 'normalized_number', 'country_code', 
            'type', 'status', 'provider', 'contact', 'device', 
            'virtual_machine', 'description'
        ]
    
    def search(self, queryset, name, value):
        """Search in multiple fields"""
        if not value.strip():
            return queryset
        return queryset.filter(
            django_filters.Q(number__icontains=value) |
            django_filters.Q(normalized_number__icontains=value) |
            django_filters.Q(description__icontains=value) |
            django_filters.Q(contact__name__icontains=value) |
            django_filters.Q(device__name__icontains=value) |
            django_filters.Q(virtual_machine__name__icontains=value)
        )
        
class PBXServerFilterSet(NetBoxModelFilterSet):
    """FilterSet for PBXServer model"""
    
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    
    type = django_filters.MultipleChoiceFilter(
        choices=PBXServer.TYPE_CHOICES,
        null_value=None
    )
    
    enabled = django_filters.BooleanFilter()
    
    class Meta:
        model = PBXServer
        fields = ['id', 'name', 'type', 'hostname', 'enabled']
    
    def search(self, queryset, name, value):
        """Search in multiple fields"""
        if not value.strip():
            return queryset
        return queryset.filter(
            django_filters.Q(name__icontains=value) |
            django_filters.Q(hostname__icontains=value) |
            django_filters.Q(description__icontains=value)
        )


class SIPTrunkFilterSet(NetBoxModelFilterSet):
    """FilterSet for SIPTrunk model"""
    
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    
    pbx_server_id = django_filters.ModelMultipleChoiceFilter(
        queryset=PBXServer.objects.all(),
        label='PBX Server',
    )
    
    provider_id = django_filters.ModelMultipleChoiceFilter(
        queryset=TelephonyProvider.objects.all(),
        label='Provider',
    )
    
    type = django_filters.MultipleChoiceFilter(
        choices=SIPTrunk.TYPE_CHOICES,
        null_value=None
    )
    
    transport = django_filters.MultipleChoiceFilter(
        choices=SIPTrunk.TRANSPORT_CHOICES,
        null_value=None
    )
    
    enabled = django_filters.BooleanFilter()
    
    class Meta:
        model = SIPTrunk
        fields = ['id', 'name', 'pbx_server', 'provider', 'type', 'host', 'transport', 'enabled']
    
    def search(self, queryset, name, value):
        """Search in multiple fields"""
        if not value.strip():
            return queryset
        return queryset.filter(
            django_filters.Q(name__icontains=value) |
            django_filters.Q(host__icontains=value) |
            django_filters.Q(description__icontains=value)
        )


class ExtensionFilterSet(NetBoxModelFilterSet):
    """FilterSet for Extension model"""
    
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    
    pbx_server_id = django_filters.ModelMultipleChoiceFilter(
        queryset=PBXServer.objects.all(),
        label='PBX Server',
    )
    
    contact_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Contact.objects.all(),
        label='Contact',
    )
    
    device_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label='Device',
    )
    
    type = django_filters.MultipleChoiceFilter(
        choices=Extension.TYPE_CHOICES,
        null_value=None
    )
    
    enabled = django_filters.BooleanFilter()
    
    class Meta:
        model = Extension
        fields = ['id', 'extension', 'pbx_server', 'type', 'contact', 'device', 'enabled']
    
    def search(self, queryset, name, value):
        """Search in multiple fields"""
        if not value.strip():
            return queryset
        return queryset.filter(
            django_filters.Q(extension__icontains=value) |
            django_filters.Q(description__icontains=value) |
            django_filters.Q(contact__name__icontains=value)
        )


class CallLogFilterSet(NetBoxModelFilterSet):
    """FilterSet for CallLog model"""
    
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    
    pbx_server_id = django_filters.ModelMultipleChoiceFilter(
        queryset=PBXServer.objects.all(),
        label='PBX Server',
    )
    
    extension_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Extension.objects.all(),
        label='Extension',
    )
    
    direction = django_filters.MultipleChoiceFilter(
        choices=CallLog.DIRECTION_CHOICES,
        null_value=None
    )
    
    status = django_filters.MultipleChoiceFilter(
        choices=CallLog.STATUS_CHOICES,
        null_value=None
    )
    
    caller_number = MultiValueCharFilter()
    called_number = MultiValueCharFilter()
    
    start_time = django_filters.DateTimeFromToRangeFilter()
    
    class Meta:
        model = CallLog
        fields = [
            'id', 'call_id', 'pbx_server', 'extension', 'direction', 
            'status', 'caller_number', 'called_number', 'start_time'
        ]
    
    def search(self, queryset, name, value):
        """Search in multiple fields"""
        if not value.strip():
            return queryset
        return queryset.filter(
            django_filters.Q(call_id__icontains=value) |
            django_filters.Q(caller_number__icontains=value) |
            django_filters.Q(called_number__icontains=value)
        )