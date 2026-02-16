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


class PBXServerView(generic.ObjectView):
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


class SIPTrunkView(generic.ObjectView):
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