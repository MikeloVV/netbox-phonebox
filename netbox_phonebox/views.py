from netbox.views import generic
from django.db.models import Count, Q, Sum
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import TemplateView, FormView, View
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import timedelta
from . import filtersets, forms, models, tables
from .pbx_utils import make_call, get_pbx_status, get_active_calls
import csv
import io

# Phone Numbers Views

class PhoneNumberListView(generic.ObjectListView):
    queryset = models.PhoneNumber.objects.all()
    table = tables.PhoneNumberTable
    filterset = filtersets.PhoneNumberFilterSet
    filterset_form = forms.PhoneNumberFilterForm


class PhoneNumberView(generic.ObjectView):
    queryset = models.PhoneNumber.objects.all()


class PhoneNumberEditView(generic.ObjectEditView):
    queryset = models.PhoneNumber.objects.all()
    form = forms.PhoneNumberForm


class PhoneNumberDeleteView(generic.ObjectDeleteView):
    queryset = models.PhoneNumber.objects.all()


class PhoneNumberBulkImportView(generic.BulkImportView):
    queryset = models.PhoneNumber.objects.all()
    model_form = forms.PhoneNumberForm  # Используем обычную форму
    table = tables.PhoneNumberTable


class PhoneNumberBulkEditView(generic.BulkEditView):
    queryset = models.PhoneNumber.objects.all()
    filterset = filtersets.PhoneNumberFilterSet
    table = tables.PhoneNumberTable
    form = forms.PhoneNumberForm


class PhoneNumberBulkDeleteView(generic.BulkDeleteView):
    queryset = models.PhoneNumber.objects.all()
    filterset = filtersets.PhoneNumberFilterSet
    table = tables.PhoneNumberTable


# Telephony Provider Views

class TelephonyProviderListView(generic.ObjectListView):
    queryset = models.TelephonyProvider.objects.all()
    table = tables.TelephonyProviderTable
    filterset = filtersets.TelephonyProviderFilterSet
    filterset_form = forms.TelephonyProviderFilterForm


class TelephonyProviderView(generic.ObjectView):
    queryset = models.TelephonyProvider.objects.all()


class TelephonyProviderEditView(generic.ObjectEditView):
    queryset = models.TelephonyProvider.objects.all()
    form = forms.TelephonyProviderForm


class TelephonyProviderDeleteView(generic.ObjectDeleteView):
    queryset = models.TelephonyProvider.objects.all()


class TelephonyProviderBulkImportView(generic.BulkImportView):
    queryset = models.TelephonyProvider.objects.all()
    model_form = forms.TelephonyProviderForm
    table = tables.TelephonyProviderTable


class TelephonyProviderBulkEditView(generic.BulkEditView):
    queryset = models.TelephonyProvider.objects.all()
    filterset = filtersets.TelephonyProviderFilterSet
    table = tables.TelephonyProviderTable
    form = forms.TelephonyProviderForm


class TelephonyProviderBulkDeleteView(generic.BulkDeleteView):
    queryset = models.TelephonyProvider.objects.all()
    filterset = filtersets.TelephonyProviderFilterSet
    table = tables.TelephonyProviderTable


# PBX Server Views

class PBXServerListView(generic.ObjectListView):
    queryset = models.PBXServer.objects.all()
    table = tables.PBXServerTable
    filterset = filtersets.PBXServerFilterSet
    filterset_form = forms.PBXServerFilterForm


class PBXServerView(generic.ObjectView):
    queryset = models.PBXServer.objects.all()
    
    def get_extra_context(self, request, instance):
        from .pbx_utils import get_pbx_status
        
        # Get PBX status
        pbx_status = get_pbx_status(instance)
        
        # Get statistics
        stats = {
            'extensions': instance.extensions.count(),
            'sip_trunks': instance.sip_trunks.count(),
            'total_calls': models.CallLog.objects.filter(pbx_server=instance).count(),
        }
        
        # Get related objects tables
        extensions_table = tables.ExtensionTable(instance.extensions.all()[:10])
        trunks_table = tables.SIPTrunkTable(instance.sip_trunks.all()[:10])
        calls_table = tables.CallLogTable(
            models.CallLog.objects.filter(pbx_server=instance).order_by('-start_time')[:10]
        )
        
        return {
            'pbx_status': pbx_status,
            'stats': stats,
            'extensions_table': extensions_table,
            'trunks_table': trunks_table,
            'calls_table': calls_table,
        }


class PBXServerEditView(generic.ObjectEditView):
    queryset = models.PBXServer.objects.all()
    form = forms.PBXServerForm


class PBXServerDeleteView(generic.ObjectDeleteView):
    queryset = models.PBXServer.objects.all()


class PBXServerBulkImportView(generic.BulkImportView):
    queryset = models.PBXServer.objects.all()
    model_form = forms.PBXServerForm
    table = tables.PBXServerTable


class PBXServerBulkEditView(generic.BulkEditView):
    queryset = models.PBXServer.objects.all()
    filterset = filtersets.PBXServerFilterSet
    table = tables.PBXServerTable
    form = forms.PBXServerForm


class PBXServerBulkDeleteView(generic.BulkDeleteView):
    queryset = models.PBXServer.objects.all()
    filterset = filtersets.PBXServerFilterSet
    table = tables.PBXServerTable


# SIP Trunk Views

class SIPTrunkListView(generic.ObjectListView):
    queryset = models.SIPTrunk.objects.all()
    table = tables.SIPTrunkTable
    filterset = filtersets.SIPTrunkFilterSet
    filterset_form = forms.SIPTrunkFilterForm


class SIPTrunkView(generic.ObjectView):
    queryset = models.SIPTrunk.objects.all()
    
    def get_extra_context(self, request, instance):
        # Get call statistics
        stats = {
            'total_calls': models.CallLog.objects.filter(
                pbx_server=instance.pbx_server
            ).count(),
            'inbound_calls': models.CallLog.objects.filter(
                pbx_server=instance.pbx_server,
                direction='inbound'
            ).count(),
            'outbound_calls': models.CallLog.objects.filter(
                pbx_server=instance.pbx_server,
                direction='outbound'
            ).count(),
        }
        
        return {
            'stats': stats,
        }


class SIPTrunkEditView(generic.ObjectEditView):
    queryset = models.SIPTrunk.objects.all()
    form = forms.SIPTrunkForm


class SIPTrunkDeleteView(generic.ObjectDeleteView):
    queryset = models.SIPTrunk.objects.all()


class SIPTrunkBulkImportView(generic.BulkImportView):
    queryset = models.SIPTrunk.objects.all()
    model_form = forms.SIPTrunkForm
    table = tables.SIPTrunkTable


class SIPTrunkBulkEditView(generic.BulkEditView):
    queryset = models.SIPTrunk.objects.all()
    filterset = filtersets.SIPTrunkFilterSet
    table = tables.SIPTrunkTable
    form = forms.SIPTrunkForm


class SIPTrunkBulkDeleteView(generic.BulkDeleteView):
    queryset = models.SIPTrunk.objects.all()
    filterset = filtersets.SIPTrunkFilterSet
    table = tables.SIPTrunkTable


# Extension Views

class ExtensionListView(generic.ObjectListView):
    queryset = models.Extension.objects.all()
    table = tables.ExtensionTable
    filterset = filtersets.ExtensionFilterSet
    filterset_form = forms.ExtensionFilterForm


class ExtensionView(generic.ObjectView):
    queryset = models.Extension.objects.all()
    
    def get_extra_context(self, request, instance):
        # Get statistics
        stats = {
            'phone_numbers': instance.phone_numbers.count(),
            'total_calls': models.CallLog.objects.filter(extension=instance).count(),
            'inbound_calls': models.CallLog.objects.filter(
                extension=instance,
                direction='inbound'
            ).count(),
            'outbound_calls': models.CallLog.objects.filter(
                extension=instance,
                direction='outbound'
            ).count(),
            'answered_calls': models.CallLog.objects.filter(
                extension=instance,
                status='answered'
            ).count(),
        }
        
        # Get related objects
        phone_numbers_table = tables.PhoneNumberTable(instance.phone_numbers.all())
        recent_calls_table = tables.CallLogTable(
            models.CallLog.objects.filter(extension=instance).order_by('-start_time')[:10]
        )
        
        return {
            'stats': stats,
            'phone_numbers_table': phone_numbers_table,
            'recent_calls_table': recent_calls_table,
        }


class ExtensionEditView(generic.ObjectEditView):
    queryset = models.Extension.objects.all()
    form = forms.ExtensionForm


class ExtensionDeleteView(generic.ObjectDeleteView):
    queryset = models.Extension.objects.all()


class ExtensionBulkImportView(generic.BulkImportView):
    queryset = models.Extension.objects.all()
    model_form = forms.ExtensionForm
    table = tables.ExtensionTable


class ExtensionBulkEditView(generic.BulkEditView):
    queryset = models.Extension.objects.all()
    filterset = filtersets.ExtensionFilterSet
    table = tables.ExtensionTable
    form = forms.ExtensionForm


class ExtensionBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Extension.objects.all()
    filterset = filtersets.ExtensionFilterSet
    table = tables.ExtensionTable


# Call Log Views

class CallLogListView(generic.ObjectListView):
    queryset = models.CallLog.objects.all()
    table = tables.CallLogTable
    filterset = filtersets.CallLogFilterSet
    filterset_form = forms.CallLogFilterForm


class CallLogView(generic.ObjectView):
    queryset = models.CallLog.objects.all()


class CallLogDeleteView(generic.ObjectDeleteView):
    queryset = models.CallLog.objects.all()


class CallLogBulkDeleteView(generic.BulkDeleteView):
    queryset = models.CallLog.objects.all()
    filterset = filtersets.CallLogFilterSet
    table = tables.CallLogTable

