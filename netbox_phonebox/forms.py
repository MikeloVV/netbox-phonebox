from django import forms

from dcim.models import Region, Site
from circuits.models import Provider
from ipam.models import IPAddress
from tenancy.models import Tenant
from netbox_secrets.models import Secret
from utilities.forms.fields import (
    CommentField,
    DynamicModelChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet
from netbox.forms import (
    NetBoxModelForm,
    NetBoxModelFilterSetForm,
    NetBoxModelBulkEditForm,
    NetBoxModelImportForm,
)

from .models import PBXServer, SIPTrunk, PhoneNumber


# ──────────────────────────────────────────────
# PBXServer
# ──────────────────────────────────────────────

class PBXServerForm(NetBoxModelForm):
    ip_address = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label="IP Address",
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
    )
    secret_login = DynamicModelChoiceField(
        queryset=Secret.objects.all(),
        required=False,
        label="Login Secret",
    )
    secret_password = DynamicModelChoiceField(
        queryset=Secret.objects.all(),
        required=False,
        label="Password Secret",
    )
    comments = CommentField()

    fieldsets = (
        FieldSet(
            "name", "domain", "ip_address", "sip_port", "site", "tenant", "description",
            name="PBX Server",
        ),
        FieldSet(
            "secret_login", "secret_password",
            name="Credentials (NetBox Secrets)",
        ),
        FieldSet("tags", name="Tags"),
    )

    class Meta:
        model = PBXServer
        fields = [
            "name",
            "domain",
            "ip_address",
            "sip_port",
            "site",
            "tenant",
            "description",
            "secret_login",
            "secret_password",
            "tags",
        ]


class PBXServerFilterForm(NetBoxModelFilterSetForm):
    model = PBXServer

    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
    )
    tag = TagFilterField(model)


class PBXServerBulkEditForm(NetBoxModelBulkEditForm):
    model = PBXServer

    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
    )
    secret_login = DynamicModelChoiceField(
        queryset=Secret.objects.all(),
        required=False,
        label="Login Secret",
    )
    secret_password = DynamicModelChoiceField(
        queryset=Secret.objects.all(),
        required=False,
        label="Password Secret",
    )
    description = forms.CharField(
        max_length=200,
        required=False,
    )

    fieldsets = (
        FieldSet("tenant", "site", "secret_login", "secret_password", "description"),
    )
    nullable_fields = ("tenant", "site", "secret_login", "secret_password", "description")


class PBXServerImportForm(NetBoxModelImportForm):
    class Meta:
        model = PBXServer
        fields = [
            "name",
            "domain",
            "sip_port",
            "description",
        ]


# ──────────────────────────────────────────────
# SIPTrunk
# ──────────────────────────────────────────────

class SIPTrunkForm(NetBoxModelForm):
    pbx_server = DynamicModelChoiceField(
        queryset=PBXServer.objects.all(),
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
    )
    secret_login = DynamicModelChoiceField(
        queryset=Secret.objects.all(),
        required=False,
        label="Login Secret",
    )
    secret_password = DynamicModelChoiceField(
        queryset=Secret.objects.all(),
        required=False,
        label="Password Secret",
    )
    comments = CommentField()

    fieldsets = (
        FieldSet(
            "name", "pbx_server", "peer_address", "peer_port", "transport", "tenant", "description",
            name="SIP Trunk",
        ),
        FieldSet(
            "secret_login", "secret_password",
            name="Credentials (NetBox Secrets)",
        ),
        FieldSet("tags", name="Tags"),
    )

    class Meta:
        model = SIPTrunk
        fields = [
            "name",
            "pbx_server",
            "peer_address",
            "peer_port",
            "transport",
            "tenant",
            "description",
            "secret_login",
            "secret_password",
            "tags",
        ]


class SIPTrunkFilterForm(NetBoxModelFilterSetForm):
    model = SIPTrunk

    pbx_server = DynamicModelChoiceField(
        queryset=PBXServer.objects.all(),
        required=False,
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
    )
    transport = forms.ChoiceField(
        choices=(("", "---------"), ("udp", "UDP"), ("tcp", "TCP"), ("tls", "TLS")),
        required=False,
    )
    tag = TagFilterField(model)


class SIPTrunkBulkEditForm(NetBoxModelBulkEditForm):
    model = SIPTrunk

    pbx_server = DynamicModelChoiceField(
        queryset=PBXServer.objects.all(),
        required=False,
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
    )
    secret_login = DynamicModelChoiceField(
        queryset=Secret.objects.all(),
        required=False,
        label="Login Secret",
    )
    secret_password = DynamicModelChoiceField(
        queryset=Secret.objects.all(),
        required=False,
        label="Password Secret",
    )
    description = forms.CharField(
        max_length=200,
        required=False,
    )

    fieldsets = (
        FieldSet("pbx_server", "tenant", "secret_login", "secret_password", "description"),
    )
    nullable_fields = ("tenant", "secret_login", "secret_password", "description")


class SIPTrunkImportForm(NetBoxModelImportForm):
    class Meta:
        model = SIPTrunk
        fields = [
            "name",
            "peer_address",
            "peer_port",
            "transport",
            "description",
        ]


# ──────────────────────────────────────────────
# PhoneNumber (без изменений)
# ──────────────────────────────────────────────

class PhoneNumberForm(NetBoxModelForm):
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
    )
    pbx_server = DynamicModelChoiceField(
        queryset=PBXServer.objects.all(),
        required=False,
        label="PBX Server",
    )
    sip_trunk = DynamicModelChoiceField(
        queryset=SIPTrunk.objects.all(),
        required=False,
        label="SIP Trunk",
    )
    provider = DynamicModelChoiceField(
        queryset=Provider.objects.all(),
        required=False,
    )
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
    )
    forward_to = DynamicModelChoiceField(
        queryset=PhoneNumber.objects.all(),
        required=False,
        label="Forward To",
    )
    comments = CommentField()

    fieldsets = (
        FieldSet("number", "label", "description", name="Phone Number"),
        FieldSet("tenant", "site", "region", "provider", name="Assignment"),
        FieldSet("pbx_server", "sip_trunk", "forward_to", name="PBX"),
        FieldSet("tags", name="Tags"),
    )

    class Meta:
        model = PhoneNumber
        fields = [
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
        ]


class PhoneNumberFilterForm(NetBoxModelFilterSetForm):
    model = PhoneNumber

    q = forms.CharField(
        required=False,
        label="Search",
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
    )
    pbx_server = DynamicModelChoiceField(
        queryset=PBXServer.objects.all(),
        required=False,
        label="PBX Server",
    )
    sip_trunk = DynamicModelChoiceField(
        queryset=SIPTrunk.objects.all(),
        required=False,
        label="SIP Trunk",
    )
    provider = DynamicModelChoiceField(
        queryset=Provider.objects.all(),
        required=False,
    )
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
    )
    tag = TagFilterField(model)


class PhoneNumberBulkEditForm(NetBoxModelBulkEditForm):
    model = PhoneNumber

    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
    )
    pbx_server = DynamicModelChoiceField(
        queryset=PBXServer.objects.all(),
        required=False,
    )
    sip_trunk = DynamicModelChoiceField(
        queryset=SIPTrunk.objects.all(),
        required=False,
    )
    provider = DynamicModelChoiceField(
        queryset=Provider.objects.all(),
        required=False,
    )
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
    )
    description = forms.CharField(
        max_length=200,
        required=False,
    )

    fieldsets = (
        FieldSet("tenant", "site", "pbx_server", "sip_trunk", "provider", "region", "description"),
    )
    nullable_fields = (
        "tenant",
        "site",
        "pbx_server",
        "sip_trunk",
        "provider",
        "region",
        "forward_to",
        "description",
    )


class PhoneNumberImportForm(NetBoxModelImportForm):
    class Meta:
        model = PhoneNumber
        fields = [
            "number",
            "label",
            "description",
        ]