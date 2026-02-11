from netbox.api.viewsets import NetBoxModelViewSet
from .. import filtersets  # Изменено с filters на filtersets
from ..models import PhoneNumber, Provider
from .serializers import PhoneNumberSerializer, ProviderSerializer


class PhoneNumberViewSet(NetBoxModelViewSet):
    """API viewset for PhoneNumber model"""
    queryset = PhoneNumber.objects.prefetch_related(
        'provider', 'contact', 'device', 'virtual_machine', 'tags'
    )
    serializer_class = PhoneNumberSerializer
    filterset_class = filtersets.PhoneNumberFilterSet  # Изменено


class ProviderViewSet(NetBoxModelViewSet):
    """API viewset for Provider model"""
    queryset = Provider.objects.prefetch_related('tags')
    serializer_class = ProviderSerializer
    filterset_class = filtersets.ProviderFilterSet  # Изменено