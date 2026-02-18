from django.contrib.contenttypes.models import ContentType
from django.db import models

from netbox.views import generic

from .models import PBXServer, SIPTrunk, PhoneNumber
from .tables import PBXServerTable, SIPTrunkTable, PhoneNumberTable
from .filtersets import PBXServerFilterSet, SIPTrunkFilterSet, PhoneNumberFilterSet
from .forms import (
    PBXServerForm,
    PBXServerFilterForm,
    PBXServerBulkEditForm,
    PBXServerImportForm,
    SIPTrunkForm,
    SIPTrunkFilterForm,
    SIPTrunkBulkEditForm,
    SIPTrunkImportForm,
    PhoneNumberForm,
    PhoneNumberFilterForm,
    PhoneNumberBulkEditForm,
    PhoneNumberImportForm,
)

try:
    from netbox_secrets.models import Secret, SessionKey
    HAS_SECRETS = True
except Exception:
    HAS_SECRETS = False


class SecretsContextMixin:
    """Mixin to inject secrets context into detail views."""

    def get_extra_context(self, request, instance):
        context = super().get_extra_context(request, instance) or {}

        if HAS_SECRETS:
            ct = ContentType.objects.get_for_model(instance)
            context["secrets"] = Secret.objects.filter(
                assigned_object_type=ct,
                assigned_object_id=instance.pk,
            ).select_related("role")
            context["content_type_id"] = ct.pk
            context["has_secrets_plugin"] = True
            context["has_session_key"] = False
            if request.user.is_authenticated:
                try:
                    context["has_session_key"] = SessionKey.objects.filter(
                        userkey__user=request.user
                    ).exists()
                except Exception:
                    context["has_session_key"] = False
        else:
            context["secrets"] = []
            context["has_secrets_plugin"] = False
            context["has_session_key"] = False

        return context


# ──────────────────────────────────────────────
# PBXServer
# ──────────────────────────────────────────────

class PBXServerListView(generic.ObjectListView):
    queryset = PBXServer.objects.annotate(
        sip_trunks_count=models.Count("sip_trunks", distinct=True),
        phone_numbers_count=models.Count("phone_numbers", distinct=True),
    )
    table = PBXServerTable
    filterset = PBXServerFilterSet
    filterset_form = PBXServerFilterForm


class PBXServerView(SecretsContextMixin, generic.ObjectView):
    queryset = PBXServer.objects.all()


class PBXServerEditView(generic.ObjectEditView):
    queryset = PBXServer.objects.all()
    form = PBXServerForm


class PBXServerDeleteView(generic.ObjectDeleteView):
    queryset = PBXServer.objects.all()


class PBXServerBulkEditView(generic.BulkEditView):
    queryset = PBXServer.objects.all()
    table = PBXServerTable
    form = PBXServerBulkEditForm
    filterset = PBXServerFilterSet


class PBXServerBulkDeleteView(generic.BulkDeleteView):
    queryset = PBXServer.objects.all()
    table = PBXServerTable
    filterset = PBXServerFilterSet


class PBXServerBulkImportView(generic.BulkImportView):
    queryset = PBXServer.objects.all()
    model_form = PBXServerImportForm


# ──────────────────────────────────────────────
# SIPTrunk
# ──────────────────────────────────────────────

class SIPTrunkListView(generic.ObjectListView):
    queryset = SIPTrunk.objects.annotate(
        phone_numbers_count=models.Count("phone_numbers", distinct=True),
    )
    table = SIPTrunkTable
    filterset = SIPTrunkFilterSet
    filterset_form = SIPTrunkFilterForm


class SIPTrunkView(SecretsContextMixin, generic.ObjectView):
    queryset = SIPTrunk.objects.all()


class SIPTrunkEditView(generic.ObjectEditView):
    queryset = SIPTrunk.objects.all()
    form = SIPTrunkForm


class SIPTrunkDeleteView(generic.ObjectDeleteView):
    queryset = SIPTrunk.objects.all()


class SIPTrunkBulkEditView(generic.BulkEditView):
    queryset = SIPTrunk.objects.all()
    table = SIPTrunkTable
    form = SIPTrunkBulkEditForm
    filterset = SIPTrunkFilterSet


class SIPTrunkBulkDeleteView(generic.BulkDeleteView):
    queryset = SIPTrunk.objects.all()
    table = SIPTrunkTable
    filterset = SIPTrunkFilterSet


class SIPTrunkBulkImportView(generic.BulkImportView):
    queryset = SIPTrunk.objects.all()
    model_form = SIPTrunkImportForm


# ──────────────────────────────────────────────
# PhoneNumber
# ──────────────────────────────────────────────

class PhoneNumberListView(generic.ObjectListView):
    queryset = PhoneNumber.objects.all()
    table = PhoneNumberTable
    filterset = PhoneNumberFilterSet
    filterset_form = PhoneNumberFilterForm


class PhoneNumberView(generic.ObjectView):
    queryset = PhoneNumber.objects.all()


class PhoneNumberEditView(generic.ObjectEditView):
    queryset = PhoneNumber.objects.all()
    form = PhoneNumberForm


class PhoneNumberDeleteView(generic.ObjectDeleteView):
    queryset = PhoneNumber.objects.all()


class PhoneNumberBulkEditView(generic.BulkEditView):
    queryset = PhoneNumber.objects.all()
    table = PhoneNumberTable
    form = PhoneNumberBulkEditForm
    filterset = PhoneNumberFilterSet


class PhoneNumberBulkDeleteView(generic.BulkDeleteView):
    queryset = PhoneNumber.objects.all()
    table = PhoneNumberTable
    filterset = PhoneNumberFilterSet


class PhoneNumberBulkImportView(generic.BulkImportView):
    queryset = PhoneNumber.objects.all()
    model_form = PhoneNumberImportForm