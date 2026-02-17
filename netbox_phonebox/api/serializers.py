from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer

from ..models import PBXServer, SIPTrunk, PhoneNumber


class PBXServerSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_phonebox-api:pbxserver-detail",
    )

    class Meta:
        model = PBXServer
        fields = [
            "id",
            "url",
            "display",
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
            "custom_fields",
            "created",
            "last_updated",
        ]
        brief_fields = ("id", "url", "display", "name")


class SIPTrunkSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_phonebox-api:siptrunk-detail",
    )

    class Meta:
        model = SIPTrunk
        fields = [
            "id",
            "url",
            "display",
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
            "custom_fields",
            "created",
            "last_updated",
        ]
        brief_fields = ("id", "url", "display", "name")


class PhoneNumberSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_phonebox-api:phonenumber-detail",
    )

    class Meta:
        model = PhoneNumber
        fields = [
            "id",
            "url",
            "display",
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
            "custom_fields",
            "created",
            "last_updated",
        ]
        brief_fields = ("id", "url", "display", "number", "label")