import django_filters
from netbox.filtersets import NetBoxModelFilterSet
from dcim.models import Device
from virtualization.models import VirtualMachine
from tenancy.models import Contact
from utilities.filters import MultiValueCharFilter
from .models import PhoneNumber, TelephonyProvider  # Изменено


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