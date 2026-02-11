from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from ..models import PhoneNumber, TelephonyProvider  # Изменено


class TelephonyProviderSerializer(NetBoxModelSerializer):  # Изменено
    """Serializer for TelephonyProvider model"""
    
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_phonebox-api:telephonyprovider-detail'  # Изменено
    )
    
    numbers_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = TelephonyProvider  # Изменено
        fields = [
            'id', 'url', 'display', 'name', 'description', 'website',
            'support_phone', 'support_email', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated', 'numbers_count'
        ]


class PhoneNumberSerializer(NetBoxModelSerializer):
    """Serializer for PhoneNumber model"""
    
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_phonebox-api:phonenumber-detail'
    )
    
    provider = TelephonyProviderSerializer(nested=True, required=False, allow_null=True)  # Изменено
    
    # Read-only computed fields
    formatted_international = serializers.CharField(read_only=True)
    formatted_national = serializers.CharField(read_only=True)
    formatted_e164 = serializers.CharField(read_only=True)
    formatted_rfc3966 = serializers.CharField(read_only=True)
    click_to_call_url = serializers.CharField(read_only=True)
    carrier_name = serializers.CharField(read_only=True)
    number_type_description = serializers.CharField(read_only=True)
    timezone = serializers.CharField(read_only=True)
    geocoding_description = serializers.CharField(read_only=True)
    assigned_to = serializers.CharField(read_only=True)
    
    class Meta:
        model = PhoneNumber
        fields = [
            'id', 'url', 'display', 'number', 'normalized_number',
            'country_code', 'type', 'status', 'provider', 'contact',
            'device', 'virtual_machine', 'description', 'comments',
            'tags', 'custom_fields', 'created', 'last_updated',
            # Computed fields
            'formatted_international', 'formatted_national',
            'formatted_e164', 'formatted_rfc3966', 'click_to_call_url',
            'carrier_name', 'number_type_description', 'timezone',
            'geocoding_description', 'assigned_to'
        ]
        read_only_fields = ['normalized_number']