from netbox.api.viewsets import NetBoxModelViewSet

from ..models import PBXServer, SIPTrunk, PhoneNumber
from ..filtersets import PBXServerFilterSet, SIPTrunkFilterSet, PhoneNumberFilterSet
from .serializers import PBXServerSerializer, SIPTrunkSerializer, PhoneNumberSerializer


class PBXServerViewSet(NetBoxModelViewSet):
    queryset = PBXServer.objects.all()
    serializer_class = PBXServerSerializer
    filterset_class = PBXServerFilterSet


class SIPTrunkViewSet(NetBoxModelViewSet):
    queryset = SIPTrunk.objects.all()
    serializer_class = SIPTrunkSerializer
    filterset_class = SIPTrunkFilterSet


class PhoneNumberViewSet(NetBoxModelViewSet):
    queryset = PhoneNumber.objects.all()
    serializer_class = PhoneNumberSerializer
    filterset_class = PhoneNumberFilterSet