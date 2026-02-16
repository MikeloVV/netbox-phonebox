from django.contrib.contenttypes.models import ContentType

from netbox.plugins import PluginTemplateExtension


class PBXServerSecretsPanel(PluginTemplateExtension):
    model = "netbox_phonebox.pbxserver"

    def right_page(self):
        obj = self.context["object"]
        ct = ContentType.objects.get_for_model(obj)

        try:
            from netbox_secrets.models import Secret

            secrets = Secret.objects.filter(
                assigned_object_type=ct,
                assigned_object_id=obj.pk,
            )
        except ImportError:
            secrets = []

        return self.render(
            "netbox_phonebox/inc/secrets_panel.html",
            extra_context={
                "secrets": secrets,
                "obj": obj,
                "content_type_id": ct.pk,
            },
        )


class SIPTrunkSecretsPanel(PluginTemplateExtension):
    model = "netbox_phonebox.siptrunk"

    def right_page(self):
        obj = self.context["object"]
        ct = ContentType.objects.get_for_model(obj)

        try:
            from netbox_secrets.models import Secret

            secrets = Secret.objects.filter(
                assigned_object_type=ct,
                assigned_object_id=obj.pk,
            )
        except ImportError:
            secrets = []

        return self.render(
            "netbox_phonebox/inc/secrets_panel.html",
            extra_context={
                "secrets": secrets,
                "obj": obj,
                "content_type_id": ct.pk,
            },
        )


template_extensions = [PBXServerSecretsPanel, SIPTrunkSecretsPanel]