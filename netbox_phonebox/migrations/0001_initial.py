from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
import taggit.managers
import utilities.json


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("circuits", "0001_initial"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("dcim", "0001_initial"),
        ("extras", "0001_initial"),
        ("ipam", "0001_initial"),
        ("tenancy", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PBXServer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=utilities.json.CustomFieldJSONEncoder,
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("domain", models.CharField(blank=True, max_length=255)),
                ("sip_port", models.PositiveIntegerField(default=5060)),
                ("description", models.CharField(blank=True, max_length=200)),
                (
                    "ip_address",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="pbx_servers",
                        to="ipam.ipaddress",
                    ),
                ),
                (
                    "site",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="pbx_servers",
                        to="dcim.site",
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="pbx_servers",
                        to="tenancy.tenant",
                    ),
                ),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "ordering": ["name"],
                "verbose_name": "PBX Server",
                "verbose_name_plural": "PBX Servers",
            },
        ),
        migrations.CreateModel(
            name="SIPTrunk",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=utilities.json.CustomFieldJSONEncoder,
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("peer_address", models.CharField(blank=True, max_length=255)),
                ("peer_port", models.PositiveIntegerField(default=5060)),
                (
                    "transport",
                    models.CharField(
                        choices=[("udp", "UDP"), ("tcp", "TCP"), ("tls", "TLS")],
                        default="udp",
                        max_length=10,
                    ),
                ),
                ("description", models.CharField(blank=True, max_length=200)),
                (
                    "pbx_server",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sip_trunks",
                        to="netbox_phonebox.pbxserver",
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="sip_trunks",
                        to="tenancy.tenant",
                    ),
                ),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "ordering": ["name"],
                "verbose_name": "SIP Trunk",
                "verbose_name_plural": "SIP Trunks",
            },
        ),
        migrations.CreateModel(
            name="PhoneNumber",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=utilities.json.CustomFieldJSONEncoder,
                    ),
                ),
                (
                    "number",
                    models.CharField(
                        max_length=32,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Enter a valid phone number.",
                                regex=r"^\+?[0-9\s\-\(\)\.]{3,30}$",
                            ),
                        ],
                    ),
                ),
                ("label", models.CharField(blank=True, max_length=100)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("assigned_object_id", models.PositiveBigIntegerField(blank=True, null=True)),
                (
                    "assigned_object_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        limit_choices_to={"model__in": ("device", "virtualmachine", "contact")},
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "forward_to",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="forwarded_from",
                        to="netbox_phonebox.phonenumber",
                    ),
                ),
                (
                    "pbx_server",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="phone_numbers",
                        to="netbox_phonebox.pbxserver",
                    ),
                ),
                (
                    "provider",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="phone_numbers",
                        to="circuits.provider",
                    ),
                ),
                (
                    "region",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="phone_numbers",
                        to="dcim.region",
                    ),
                ),
                (
                    "site",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="phone_numbers",
                        to="dcim.site",
                    ),
                ),
                (
                    "sip_trunk",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="phone_numbers",
                        to="netbox_phonebox.siptrunk",
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="phone_numbers",
                        to="tenancy.tenant",
                    ),
                ),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "ordering": ["number"],
                "verbose_name": "Phone Number",
                "verbose_name_plural": "Phone Numbers",
            },
        ),
    ]