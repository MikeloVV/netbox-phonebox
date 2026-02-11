from netbox.api.viewsets import NetBoxModelViewSet
from .. import filtersets
from ..models import PhoneNumber, TelephonyProvider  # Изменено
from .serializers import PhoneNumberSerializer, TelephonyProviderSerializer  # Изменено


class PhoneNumberViewSet(NetBoxModelViewSet):
    """API viewset for PhoneNumber model"""
    queryset = PhoneNumber.objects.prefetch_related(
        'provider', 'contact', 'device', 'virtual_machine', 'tags'
    )
    serializer_class = PhoneNumberSerializer
    filterset_class = filtersets.PhoneNumberFilterSet


class TelephonyProviderViewSet(NetBoxModelViewSet):  # Изменено
    """API viewset for TelephonyProvider model"""
    queryset = TelephonyProvider.objects.prefetch_related('tags')  # Изменено
    serializer_class = TelephonyProviderSerializer  # Изменено
    filterset_class = filtersets.TelephonyProviderFilterSet  # Изменено