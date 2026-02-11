from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from ..models import (
    PhoneNumber, TelephonyProvider, PBXServer, 
    SIPTrunk, Extension, CallLog
)


class TelephonyProviderSerializer(NetBoxModelSerializer):
    """Serializer for TelephonyProvider model"""
    
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_phonebox-api:telephonyprovider-detail'
    )
    
    numbers_count = serializers.IntegerField(read_only=True)
    active_numbers_count = serializers.IntegerField(read_only=True)
    reserved_numbers_count = serializers.IntegerField(read_only=True)
    deprecated_numbers_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = TelephonyProvider
        fields = [
            'id', 'url', 'display', 'name', 'description', 'website',
            'support_phone', 'support_email', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated', 
            'numbers_count', 'active_numbers_count', 
            'reserved_numbers_count', 'deprecated_numbers_count'
        ]


class PBXServerSerializer(NetBoxModelSerializer):
    """Serializer for PBXServer model"""
    
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_phonebox-api:pbxserver-detail'
    )
    
    connection_string = serializers.CharField(read_only=True)
    
    class Meta:
        model = PBXServer
        fields = [
            'id', 'url', 'display', 'name', 'type', 'hostname', 
            'ami_port', 'ami_username', 'ami_secret', 'web_url',
            'enabled', 'description', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated',
            'connection_string'
        ]
        extra_kwargs = {
            'ami_secret': {'write_only': True}
        }


class SIPTrunkSerializer(NetBoxModelSerializer):
    """Serializer for SIPTrunk model"""
    
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_phonebox-api:siptrunk-detail'
    )
    
    pbx_server = PBXServerSerializer(nested=True, read_only=True)
    provider = TelephonyProviderSerializer(nested=True, required=False, allow_null=True, read_only=True)
    
    class Meta:
        model = SIPTrunk
        fields = [
            'id', 'url', 'display', 'name', 'pbx_server', 'provider',
            'type', 'host', 'port', 'transport', 'username', 'secret',
            'context', 'enabled', 'description', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated'
        ]
        extra_kwargs = {
            'secret': {'write_only': True}
        }


class ExtensionSerializer(NetBoxModelSerializer):
    """Serializer for Extension model"""
    
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_phonebox-api:extension-detail'
    )
    
    pbx_server = PBXServerSerializer(nested=True, read_only=True)
    
    class Meta:
        model = Extension
        fields = [
            'id', 'url', 'display', 'extension', 'pbx_server', 'type',
            'contact', 'device', 'secret', 'enabled', 'description',
            'comments', 'tags', 'custom_fields', 'created', 'last_updated'
        ]
        extra_kwargs = {
            'secret': {'write_only': True}
        }


class CallLogSerializer(NetBoxModelSerializer):
    """Serializer for CallLog model"""
    
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_phonebox-api:calllog-detail'
    )
    
    pbx_server = PBXServerSerializer(nested=True, read_only=True)
    extension = ExtensionSerializer(nested=True, required=False, allow_null=True, read_only=True)
    
    duration_formatted = serializers.CharField(read_only=True)
    
    class Meta:
        model = CallLog
        fields = [
            'id', 'url', 'display', 'call_id', 'pbx_server', 'direction',
            'caller_number', 'called_number', 'extension', 'status',
            'start_time', 'answer_time', 'end_time', 'duration',
            'duration_formatted', 'recording_url', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated'
        ]


class PhoneNumberSerializer(NetBoxModelSerializer):
    """Serializer for PhoneNumber model"""
    
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_phonebox-api:phonenumber-detail'
    )
    
    provider = TelephonyProviderSerializer(nested=True, required=False, allow_null=True, read_only=True)
    extension = ExtensionSerializer(nested=True, required=False, allow_null=True, read_only=True)
    
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
    call_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = PhoneNumber
        fields = [
            'id', 'url', 'display', 'number', 'normalized_number',
            'country_code', 'type', 'status', 'provider', 'extension',
            'contact', 'device', 'virtual_machine', 'description', 'comments',
            'tags', 'custom_fields', 'created', 'last_updated',
            # Computed fields
            'formatted_international', 'formatted_national',
            'formatted_e164', 'formatted_rfc3966', 'click_to_call_url',
            'carrier_name', 'number_type_description', 'timezone',
            'geocoding_description', 'assigned_to', 'call_count'
        ]
        read_only_fields = ['normalized_number']