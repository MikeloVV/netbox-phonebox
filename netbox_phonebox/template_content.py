from django.contrib.contenttypes.models import ContentType

from netbox.plugins import PluginTemplateExtension

try:
    from netbox_secrets.models import Secret, SessionKey
    HAS_SECRETS = True
except ImportError:
    HAS_SECRETS = False


class PBXServerSecretsPanel(PluginTemplateExtension):
    model = "netbox_phonebox.pbxserver"

    def right_page(self):
        if not HAS_SECRETS:
            return ""

        obj = self.context["object"]
        request = self.context["request"]
        ct = ContentType.objects.get_for_model(obj)

        secrets = Secret.objects.filter(
            assigned_object_type=ct,
            assigned_object_id=obj.pk,
        ).select_related("role")

        # Check if user has active session key
        has_session_key = False
        if request.user.is_authenticated:
            has_session_key = SessionKey.objects.filter(
                userkey__user=request.user
            ).exists()

        return self.render(
            "netbox_phonebox/inc/secrets_panel.html",
            extra_context={
                "secrets": secrets,
                "parent_object": obj,
                "content_type_id": ct.pk,
                "has_session_key": has_session_key,
            },
        )


class SIPTrunkSecretsPanel(PluginTemplateExtension):
    model = "netbox_phonebox.siptrunk"

    def right_page(self):
        if not HAS_SECRETS:
            return ""

        obj = self.context["object"]
        request = self.context["request"]
        ct = ContentType.objects.get_for_model(obj)

        secrets = Secret.objects.filter(
            assigned_object_type=ct,
            assigned_object_id=obj.pk,
        ).select_related("role")

        has_session_key = False
        if request.user.is_authenticated:
            has_session_key = SessionKey.objects.filter(
                userkey__user=request.user
            ).exists()

        return self.render(
            "netbox_phonebox/inc/secrets_panel.html",
            extra_context={
                "secrets": secrets,
                "parent_object": obj,
                "content_type_id": ct.pk,
                "has_session_key": has_session_key,
            },
        )


template_extensions = [PBXServerSecretsPanel, SIPTrunkSecretsPanel]