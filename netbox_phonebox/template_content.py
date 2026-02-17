from django.contrib.contenttypes.models import ContentType

from netbox.plugins import PluginTemplateExtension

try:
    from netbox_secrets.models import Secret
    HAS_SECRETS = True
except ImportError:
    HAS_SECRETS = False


class PBXServerSecretsPanel(PluginTemplateExtension):
    model = "netbox_phonebox.pbxserver"

    def right_page(self):
        if not HAS_SECRETS:
            return ""

        obj = self.context["object"]
        ct = ContentType.objects.get_for_model(obj)

        secrets = Secret.objects.filter(
            assigned_object_type=ct,
            assigned_object_id=obj.pk,
        )

        return self.render(
            "netbox_phonebox/inc/secrets_panel.html",
            extra_context={
                "secrets": secrets,
                "parent_object": obj,
                "content_type_id": ct.pk,
            },
        )


class SIPTrunkSecretsPanel(PluginTemplateExtension):
    model = "netbox_phonebox.siptrunk"

    def right_page(self):
        if not HAS_SECRETS:
            return ""

        obj = self.context["object"]
        ct = ContentType.objects.get_for_model(obj)

        secrets = Secret.objects.filter(
            assigned_object_type=ct,
            assigned_object_id=obj.pk,
        )

        return self.render(
            "netbox_phonebox/inc/secrets_panel.html",
            extra_context={
                "secrets": secrets,
                "parent_object": obj,
                "content_type_id": ct.pk,
            },
        )


template_extensions = [PBXServerSecretsPanel, SIPTrunkSecretsPanel]