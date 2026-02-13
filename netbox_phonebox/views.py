from django.shortcuts import render
from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from netbox.views import generic
from . import filtersets, forms, models, tables


# Dashboard
class PhoneNumberDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'netbox_phonebox/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistics
        context['total_numbers'] = models.PhoneNumber.objects.count()
        context['total_providers'] = models.TelephonyProvider.objects.count()
        context['total_pbx_servers'] = models.PBXServer.objects.count()
        context['total_extensions'] = models.Extension.objects.count()
        context['total_trunks'] = models.SIPTrunk.objects.count()
        context['total_calls'] = models.CallLog.objects.count()
        
        # Phone number statistics by type
        context['mobile_numbers'] = models.PhoneNumber.objects.filter(type='mobile').count()
        context['landline_numbers'] = models.PhoneNumber.objects.filter(type='landline').count()
        context['voip_numbers'] = models.PhoneNumber.objects.filter(type='voip').count()
        
        # Phone number statistics by status
        context['active_numbers'] = models.PhoneNumber.objects.filter(status='active').count()
        context['reserved_numbers'] = models.PhoneNumber.objects.filter(status='reserved').count()
        context['inactive_numbers'] = models.PhoneNumber.objects.filter(status='inactive').count()
        
        return context


# Phone Numbers
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
    model_form = forms.PhoneNumberForm
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


# Telephony Providers
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


# PBX Servers
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
        # ИСПРАВЛЕНИЕ: Сначала order_by, потом срез
        extensions_qs = instance.extensions.all().order_by('extension')[:10]
        extensions_table = tables.ExtensionTable(list(extensions_qs))
        
        trunks_qs = instance.sip_trunks.all().order_by('name')[:10]
        trunks_table = tables.SIPTrunkTable(list(trunks_qs))
        
        calls_qs = models.CallLog.objects.filter(pbx_server=instance).order_by('-start_time')[:10]
        calls_table = tables.CallLogTable(list(calls_qs))
        
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


# SIP Trunks
class SIPTrunkListView(generic.ObjectListView):
    queryset = models.SIPTrunk.objects.all()
    table = tables.SIPTrunkTable
    filterset = filtersets.SIPTrunkFilterSet
    filterset_form = forms.SIPTrunkFilterForm


class SIPTrunkView(generic.ObjectView):
    queryset = models.SIPTrunk.objects.all()
    
    def get_extra_context(self, request, instance):
        # Get call statistics (if available)
        stats = {
            'total_calls': 0,
            'inbound_calls': 0,
            'outbound_calls': 0,
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


# Extensions
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
        # ИСПРАВЛЕНИЕ: Преобразуем в list после среза
        phone_numbers_qs = instance.phone_numbers.all().order_by('number')
        phone_numbers_table = tables.PhoneNumberTable(list(phone_numbers_qs))
        
        recent_calls_qs = models.CallLog.objects.filter(extension=instance).order_by('-start_time')[:10]
        recent_calls_table = tables.CallLogTable(list(recent_calls_qs))
        
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


# Call Logs
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


# Call Statistics
class CallStatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'netbox_phonebox/call_statistics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Overall statistics
        context['total_calls'] = models.CallLog.objects.count()
        context['answered_calls'] = models.CallLog.objects.filter(status='answered').count()
        context['missed_calls'] = models.CallLog.objects.filter(status='no_answer').count()
        context['failed_calls'] = models.CallLog.objects.filter(status='failed').count()
        
        # Direction statistics
        context['inbound_calls'] = models.CallLog.objects.filter(direction='inbound').count()
        context['outbound_calls'] = models.CallLog.objects.filter(direction='outbound').count()
        context['internal_calls'] = models.CallLog.objects.filter(direction='internal').count()
        
        # Recent calls
        context['recent_calls'] = models.CallLog.objects.order_by('-start_time')[:20]
        
        return context


# Make Call
class MakeCallView(LoginRequiredMixin, FormView):
    template_name = 'netbox_phonebox/make_call.html'
    form_class = forms.MakeCallForm
    success_url = reverse_lazy('plugins:netbox_phonebox:dashboard')
    
    def get_initial(self):
        initial = super().get_initial()
        
        # Pre-fill from GET parameters
        if 'extension' in self.request.GET:
            try:
                extension_id = int(self.request.GET['extension'])
                extension = models.Extension.objects.get(pk=extension_id)
                initial['pbx_server'] = extension.pbx_server
                initial['from_extension'] = extension
            except (ValueError, models.Extension.DoesNotExist):
                pass
        
        if 'number' in self.request.GET:
            initial['to_number'] = self.request.GET['number']
        
        return initial
    
    def form_valid(self, form):
        from .pbx_utils import initiate_call
        
        pbx_server = form.cleaned_data['pbx_server']
        from_extension = form.cleaned_data['from_extension']
        to_number = form.cleaned_data['to_number']
        caller_id = form.cleaned_data.get('caller_id', '')
        
        # Initiate call
        result = initiate_call(
            pbx_server=pbx_server,
            from_extension=from_extension.extension,
            to_number=to_number,
            caller_id=caller_id or from_extension.extension
        )
        
        # Show result message
        if result.get('success'):
            from django.contrib import messages
            messages.success(
                self.request,
                f"Call initiated successfully: {from_extension.extension} → {to_number}"
            )
        else:
            from django.contrib import messages
            messages.error(
                self.request,
                f"Failed to initiate call: {result.get('message', 'Unknown error')}"
            )
        
        return super().form_valid(form)