import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse

from netbox.models import NetBoxModel
from django.db import models
from netbox_secrets.models import Secret


phone_number_validator = RegexValidator(
    regex=r"^\+?[0-9\s\-\(\)\.]{3,30}$",
    message="Enter a valid phone number. Examples: +74951234567, +1 (212) 555-1234",
)


def validate_phone_number(value: str) -> None:
    """Additional phone number validation."""
    digits = re.sub(r"[^\d]", "", value)
    if len(digits) < 3:
        raise ValidationError("Phone number must contain at least 3 digits.")
    if len(digits) > 15:
        raise ValidationError("Phone number must not exceed 15 digits (E.164).")


class PBXServer(NetBoxModel):
    """PBX Server — IP-АТС."""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Name",
    )
    domain = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Domain / FQDN",
    )
    ip_address = models.ForeignKey(
        to="ipam.IPAddress",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="pbx_servers",
        verbose_name="IP Address",
    )
    sip_port = models.PositiveIntegerField(
        default=5060,
        verbose_name="SIP Port",
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Description",
    )
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="pbx_servers",
        verbose_name="Tenant",
    )
    site = models.ForeignKey(
        to="dcim.Site",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="pbx_servers",
        verbose_name="Site",
    )

    # Credentials via netbox-secrets
    secret_login = models.ForeignKey(
        to="netbox_secrets.Secret",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="pbxserver_logins",
        verbose_name="Login Secret",
        help_text="Secret containing the login/username.",
    )
    secret_password = models.ForeignKey(
        to="netbox_secrets.Secret",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="pbxserver_passwords",
        verbose_name="Password Secret",
        help_text="Secret containing the password.",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "PBX Server"
        verbose_name_plural = "PBX Servers"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_phonebox:pbxserver", args=[self.pk])


class SIPTrunk(NetBoxModel):
    """SIP Trunk — SIP-транк между АТС или к провайдеру."""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Name",
    )
    pbx_server = models.ForeignKey(
        to="netbox_phonebox.PBXServer",
        on_delete=models.CASCADE,
        related_name="sip_trunks",
        verbose_name="PBX Server",
    )
    peer_address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Peer Address / FQDN",
        help_text="Remote SIP peer address or FQDN.",
    )
    peer_port = models.PositiveIntegerField(
        default=5060,
        verbose_name="Peer Port",
    )
    transport = models.CharField(
        max_length=10,
        choices=(
            ("udp", "UDP"),
            ("tcp", "TCP"),
            ("tls", "TLS"),
        ),
        default="udp",
        verbose_name="Transport",
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Description",
    )
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="sip_trunks",
        verbose_name="Tenant",
    )

    # Credentials via netbox-secrets
    secret_login = models.ForeignKey(
        to="netbox_secrets.Secret",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="siptrunk_logins",
        verbose_name="Login Secret",
        help_text="Secret containing the login/username.",
    )
    secret_password = models.ForeignKey(
        to="netbox_secrets.Secret",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="siptrunk_passwords",
        verbose_name="Password Secret",
        help_text="Secret containing the password.",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "SIP Trunk"
        verbose_name_plural = "SIP Trunks"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_phonebox:siptrunk", args=[self.pk])


class PhoneNumber(NetBoxModel):
    """Phone Number — телефонный номер."""

    number = models.CharField(
        max_length=32,
        unique=True,
        verbose_name="Number",
        validators=[phone_number_validator, validate_phone_number],
    )
    label = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Label",
        help_text="Friendly label, e.g. 'Reception', 'Fax'.",
    )
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="phone_numbers",
        verbose_name="Tenant",
    )
    site = models.ForeignKey(
        to="dcim.Site",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="phone_numbers",
        verbose_name="Site",
    )
    pbx_server = models.ForeignKey(
        to="netbox_phonebox.PBXServer",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="phone_numbers",
        verbose_name="PBX Server",
    )
    sip_trunk = models.ForeignKey(
        to="netbox_phonebox.SIPTrunk",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="phone_numbers",
        verbose_name="SIP Trunk",
    )
    provider = models.ForeignKey(
        to="circuits.Provider",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="phone_numbers",
        verbose_name="Provider",
    )
    region = models.ForeignKey(
        to="dcim.Region",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="phone_numbers",
        verbose_name="Region",
    )
    assigned_object_type = models.ForeignKey(
        to="contenttypes.ContentType",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to={
            "model__in": ("device", "virtualmachine", "contact"),
        },
        verbose_name="Assigned Object Type",
    )
    assigned_object_id = models.PositiveBigIntegerField(
        blank=True,
        null=True,
        verbose_name="Assigned Object ID",
    )
    forward_to = models.ForeignKey(
        to="self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="forwarded_from",
        verbose_name="Forward To",
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Description",
    )

    class Meta:
        ordering = ["number"]
        verbose_name = "Phone Number"
        verbose_name_plural = "Phone Numbers"

    def __str__(self):
        if self.label:
            return f"{self.number} ({self.label})"
        return self.number

    def get_absolute_url(self):
        return reverse("plugins:netbox_phonebox:phonenumber", args=[self.pk])

    @property
    def assigned_object(self):
        if self.assigned_object_type and self.assigned_object_id:
            model_class = self.assigned_object_type.model_class()
            if model_class:
                try:
                    return model_class.objects.get(pk=self.assigned_object_id)
                except model_class.DoesNotExist:
                    return None
        return None

    def clean(self):
        super().clean()
        if self.number:
            self.number = self.number.strip()