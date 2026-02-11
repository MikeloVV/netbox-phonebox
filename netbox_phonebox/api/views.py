from netbox.api.viewsets import NetBoxModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .. import filtersets
from ..models import (
    PhoneNumber, TelephonyProvider, PBXServer, 
    SIPTrunk, Extension, CallLog
)
from ..pbx_utils import make_call, get_pbx_status, get_active_calls
from .serializers import (
    PhoneNumberSerializer, TelephonyProviderSerializer,
    PBXServerSerializer, SIPTrunkSerializer,
    ExtensionSerializer, CallLogSerializer
)


class PhoneNumberViewSet(NetBoxModelViewSet):
    """API viewset for PhoneNumber model"""
    queryset = PhoneNumber.objects.prefetch_related(
        'provider', 'extension', 'contact', 'device', 'virtual_machine', 'tags'
    )
    serializer_class = PhoneNumberSerializer
    filterset_class = filtersets.PhoneNumberFilterSet


class TelephonyProviderViewSet(NetBoxModelViewSet):
    """API viewset for TelephonyProvider model"""
    queryset = TelephonyProvider.objects.prefetch_related('tags')
    serializer_class = TelephonyProviderSerializer
    filterset_class = filtersets.TelephonyProviderFilterSet


class PBXServerViewSet(NetBoxModelViewSet):
    """API viewset for PBXServer model"""
    queryset = PBXServer.objects.prefetch_related('tags')
    serializer_class = PBXServerSerializer
    filterset_class = filtersets.PBXServerFilterSet
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get PBX server status"""
        pbx_server = self.get_object()
        status_info = get_pbx_status(pbx_server)
        return Response(status_info)
    
    @action(detail=True, methods=['get'])
    def active_calls(self, request, pk=None):
        """Get active calls on PBX server"""
        pbx_server = self.get_object()
        calls = get_active_calls(pbx_server)
        return Response(calls)


class SIPTrunkViewSet(NetBoxModelViewSet):
    """API viewset for SIPTrunk model"""
    queryset = SIPTrunk.objects.prefetch_related('pbx_server', 'provider', 'tags')
    serializer_class = SIPTrunkSerializer
    filterset_class = filtersets.SIPTrunkFilterSet


class ExtensionViewSet(NetBoxModelViewSet):
    """API viewset for Extension model"""
    queryset = Extension.objects.prefetch_related('pbx_server', 'contact', 'device', 'tags')
    serializer_class = ExtensionSerializer
    filterset_class = filtersets.ExtensionFilterSet
    
    @action(detail=True, methods=['post'])
    def make_call(self, request, pk=None):
        """Initiate a call from this extension"""
        extension = self.get_object()
        to_number = request.data.get('to_number')
        
        if not to_number:
            return Response(
                {'error': 'to_number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = make_call(extension.pbx_server, extension, to_number)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


class CallLogViewSet(NetBoxModelViewSet):
    """API viewset for CallLog model"""
    queryset = CallLog.objects.prefetch_related('pbx_server', 'extension', 'tags')
    serializer_class = CallLogSerializer
    filterset_class = filtersets.CallLogFilterSet