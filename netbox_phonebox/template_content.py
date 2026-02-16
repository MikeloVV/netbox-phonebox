from netbox.plugins import PluginTemplateExtension

from netbox_secrets.models import Secret


class PBXServerSecretsPanel(PluginTemplateExtension):
    """Добавляет панель Secrets на страницу PBX Server."""

    model = "netbox_phonebox.pbxserver"

    def right_page(self):
        obj = self.context["object"]
        request = self.context["request"]

        secrets = Secret.objects.filter(
            assigned_object_type__app_label=obj._meta.app_label,
            assigned_object_type__model=obj._meta.model_name,
            assigned_object_id=obj.pk,
        )

        return self.render(
            "netbox_phonebox/inc/secrets_panel.html",
            extra_context={
                "secrets": secrets,
                "object": obj,
            },
        )


class SIPTrunkSecretsPanel(PluginTemplateExtension):
    """Добавляет панель Secrets на страницу SIP Trunk."""

    model = "netbox_phonebox.siptrunk"

    def right_page(self):
        obj = self.context["object"]
        request = self.context["request"]

        secrets = Secret.objects.filter(
            assigned_object_type__app_label=obj._meta.app_label,
            assigned_object_type__model=obj._meta.model_name,
            assigned_object_id=obj.pk,
        )

        return self.render(
            "netbox_phonebox/inc/secrets_panel.html",
            extra_context={
                "secrets": secrets,
                "object": obj,
            },
        )


template_extensions = [PBXServerSecretsPanel, SIPTrunkSecretsPanel]