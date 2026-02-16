import django_tables2 as tables

from netbox.tables import NetBoxTable, columns

from .models import PBXServer, SIPTrunk, PhoneNumber


class PBXServerTable(NetBoxTable):
    name = tables.Column(
        linkify=True,
    )
    ip_address = tables.Column(
        linkify=True,
        verbose_name="IP Address",
    )
    site = tables.Column(
        linkify=True,
    )
    tenant = tables.Column(
        linkify=True,
    )
    sip_trunks_count = columns.LinkedCountColumn(
        viewname="plugins:netbox_phonebox:siptrunk_list",
        url_params={"pbx_server": "pk"},
        verbose_name="SIP Trunks",
    )
    phone_numbers_count = columns.LinkedCountColumn(
        viewname="plugins:netbox_phonebox:phonenumber_list",
        url_params={"pbx_server": "pk"},
        verbose_name="Phone Numbers",
    )
    tags = columns.TagColumn()

    class Meta(NetBoxTable.Meta):
        model = PBXServer
        fields = (
            "pk",
            "id",
            "name",
            "domain",
            "ip_address",
            "sip_port",
            "site",
            "tenant",
            "sip_trunks_count",
            "phone_numbers_count",
            "description",
            "tags",
        )
        default_columns = (
            "name",
            "domain",
            "ip_address",
            "sip_port",
            "site",
            "tenant",
            "sip_trunks_count",
            "description",
        )


class SIPTrunkTable(NetBoxTable):
    name = tables.Column(
        linkify=True,
    )
    pbx_server = tables.Column(
        linkify=True,
        verbose_name="PBX Server",
    )
    tenant = tables.Column(
        linkify=True,
    )
    phone_numbers_count = columns.LinkedCountColumn(
        viewname="plugins:netbox_phonebox:phonenumber_list",
        url_params={"sip_trunk": "pk"},
        verbose_name="Phone Numbers",
    )
    tags = columns.TagColumn()

    class Meta(NetBoxTable.Meta):
        model = SIPTrunk
        fields = (
            "pk",
            "id",
            "name",
            "pbx_server",
            "peer_address",
            "peer_port",
            "transport",
            "tenant",
            "phone_numbers_count",
            "description",
            "tags",
        )
        default_columns = (
            "name",
            "pbx_server",
            "peer_address",
            "transport",
            "tenant",
            "phone_numbers_count",
            "description",
        )


class PhoneNumberTable(NetBoxTable):
    number = tables.Column(
        linkify=True,
    )
    tenant = tables.Column(
        linkify=True,
    )
    site = tables.Column(
        linkify=True,
    )
    pbx_server = tables.Column(
        linkify=True,
        verbose_name="PBX Server",
    )
    sip_trunk = tables.Column(
        linkify=True,
        verbose_name="SIP Trunk",
    )
    provider = tables.Column(
        linkify=True,
    )
    region = tables.Column(
        linkify=True,
    )
    forward_to = tables.Column(
        linkify=True,
        verbose_name="Forward To",
    )
    tags = columns.TagColumn()

    class Meta(NetBoxTable.Meta):
        model = PhoneNumber
        fields = (
            "pk",
            "id",
            "number",
            "label",
            "tenant",
            "site",
            "pbx_server",
            "sip_trunk",
            "provider",
            "region",
            "forward_to",
            "description",
            "tags",
        )
        default_columns = (
            "number",
            "label",
            "tenant",
            "site",
            "pbx_server",
            "provider",
            "description",
        )