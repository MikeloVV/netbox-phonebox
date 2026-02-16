import django_filters

from django.db.models import Q

from circuits.models import Provider
from dcim.models import Region, Site
from tenancy.models import Tenant
from netbox.filtersets import NetBoxModelFilterSet

from .models import PBXServer, SIPTrunk, PhoneNumber


class PBXServerFilterSet(NetBoxModelFilterSet):
    tenant = django_filters.ModelChoiceFilter(
        queryset=Tenant.objects.all(),
    )
    site = django_filters.ModelChoiceFilter(
        queryset=Site.objects.all(),
    )

    class Meta:
        model = PBXServer
        fields = ["id", "name", "domain", "sip_port", "tenant", "site"]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
            | Q(domain__icontains=value)
            | Q(description__icontains=value)
        )


class SIPTrunkFilterSet(NetBoxModelFilterSet):
    pbx_server = django_filters.ModelChoiceFilter(
        queryset=PBXServer.objects.all(),
    )
    tenant = django_filters.ModelChoiceFilter(
        queryset=Tenant.objects.all(),
    )
    transport = django_filters.ChoiceFilter(
        choices=(("udp", "UDP"), ("tcp", "TCP"), ("tls", "TLS")),
    )

    class Meta:
        model = SIPTrunk
        fields = ["id", "name", "pbx_server", "transport", "tenant"]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
            | Q(peer_address__icontains=value)
            | Q(description__icontains=value)
        )


class PhoneNumberFilterSet(NetBoxModelFilterSet):
    tenant = django_filters.ModelChoiceFilter(
        queryset=Tenant.objects.all(),
    )
    site = django_filters.ModelChoiceFilter(
        queryset=Site.objects.all(),
    )
    pbx_server = django_filters.ModelChoiceFilter(
        queryset=PBXServer.objects.all(),
    )
    sip_trunk = django_filters.ModelChoiceFilter(
        queryset=SIPTrunk.objects.all(),
    )
    provider = django_filters.ModelChoiceFilter(
        queryset=Provider.objects.all(),
    )
    region = django_filters.ModelChoiceFilter(
        queryset=Region.objects.all(),
    )

    class Meta:
        model = PhoneNumber
        fields = [
            "id",
            "number",
            "label",
            "tenant",
            "site",
            "pbx_server",
            "sip_trunk",
            "provider",
            "region",
        ]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(number__icontains=value)
            | Q(label__icontains=value)
            | Q(description__icontains=value)
        )