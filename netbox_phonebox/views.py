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



class PhoneNumberDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard with phone number and PBX statistics"""
    
    template_name = 'netbox_phonebox/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Phone Number Statistics
        total = models.PhoneNumber.objects.count()
        active = models.PhoneNumber.objects.filter(status='active').count()
        reserved = models.PhoneNumber.objects.filter(status='reserved').count()
        deprecated = models.PhoneNumber.objects.filter(status='deprecated').count()
        
        # Type statistics
        type_stats = models.PhoneNumber.objects.values('type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Provider statistics
        provider_stats = models.PhoneNumber.objects.filter(
            provider__isnull=False
        ).values(
            'provider__name', 'provider__id'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Country statistics
        country_stats = models.PhoneNumber.objects.exclude(
            country_code=''
        ).values('country_code').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Unassigned numbers
        unassigned = models.PhoneNumber.objects.filter(
            contact__isnull=True,
            device__isnull=True,
            virtual_machine__isnull=True
        ).count()
        
        # Recent numbers
        recent_numbers = models.PhoneNumber.objects.order_by('-created')[:10]
        
        # Provider count
        providers_count = models.TelephonyProvider.objects.count()
        
        # PBX Statistics
        pbx_servers_count = models.PBXServer.objects.count()
        pbx_servers_online = 0
        for pbx in models.PBXServer.objects.filter(enabled=True):
            status = get_pbx_status(pbx)
            if status.get('online'):
                pbx_servers_online += 1
        
        extensions_count = models.Extension.objects.count()
        active_extensions = models.Extension.objects.filter(enabled=True).count()
        
        trunks_count = models.SIPTrunk.objects.count()
        active_trunks = models.SIPTrunk.objects.filter(enabled=True).count()
        
        # Call Statistics
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        total_calls = models.CallLog.objects.count()
        calls_today = models.CallLog.objects.filter(
            start_time__date=today
        ).count()
        calls_this_week = models.CallLog.objects.filter(
            start_time__date__gte=week_ago
        ).count()
        
        answered_calls = models.CallLog.objects.filter(
            status='answered'
        ).count()
        
        answer_rate = (answered_calls / total_calls * 100) if total_calls > 0 else 0
        
        # Recent calls
        recent_calls = models.CallLog.objects.order_by('-start_time')[:10]
        
        # Chart data for providers
        provider_chart_data = []
        provider_chart_labels = []
        for stat in provider_stats:
            provider_chart_labels.append(stat['provider__name'])
            provider_chart_data.append(stat['count'])
        
        # Chart data for types
        type_chart_data = []
        type_chart_labels = []
        for stat in type_stats:
            type_chart_labels.append(dict(models.PhoneNumber.TYPE_CHOICES).get(stat['type'], stat['type']))
            type_chart_data.append(stat['count'])
        
        context.update({
            # Phone Numbers
            'total': total,
            'active': active,
            'reserved': reserved,
            'deprecated': deprecated,
            'unassigned': unassigned,
            'providers_count': providers_count,
            'type_stats': type_stats,
            'provider_stats': provider_stats,
            'country_stats': country_stats,
            'recent_numbers': recent_numbers,
            'provider_chart_data': provider_chart_data,
            'provider_chart_labels': provider_chart_labels,
            'type_chart_data': type_chart_data,
            'type_chart_labels': type_chart_labels,
            
            # PBX
            'pbx_servers_count': pbx_servers_count,
            'pbx_servers_online': pbx_servers_online,
            'extensions_count': extensions_count,
            'active_extensions': active_extensions,
            'trunks_count': trunks_count,
            'active_trunks': active_trunks,
            
            # Calls
            'total_calls': total_calls,
            'calls_today': calls_today,
            'calls_this_week': calls_this_week,
            'answered_calls': answered_calls,
            'answer_rate': round(answer_rate, 2),
            'recent_calls': recent_calls,
        })
        
        return context
        
class PhoneNumberListView(generic.ObjectListView):
    """List view for phone numbers"""
    queryset = models.PhoneNumber.objects.all()
    table = tables.PhoneNumberTable
    filterset = filtersets.PhoneNumberFilterSet
    filterset_form = forms.PhoneNumberFilterForm


class PhoneNumberView(generic.ObjectView):
    """Detail view for phone number"""
    queryset = models.PhoneNumber.objects.all()


class PhoneNumberEditView(generic.ObjectEditView):
    """Edit view for phone number"""
    queryset = models.PhoneNumber.objects.all()
    form = forms.PhoneNumberForm


class PhoneNumberDeleteView(generic.ObjectDeleteView):
    """Delete view for phone number"""
    queryset = models.PhoneNumber.objects.all()


class PhoneNumberBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for phone numbers"""
    queryset = models.PhoneNumber.objects.all()
    table = tables.PhoneNumberTable


class PhoneNumberImportView(LoginRequiredMixin, FormView):
    """Import phone numbers from CSV file"""
    
    template_name = 'netbox_phonebox/phonenumber_import.html'
    form_class = forms.PhoneNumberImportForm
    
    def form_valid(self, form):
        csv_file = form.cleaned_data['csv_file']
        update_existing = form.cleaned_data['update_existing']
        
        try:
            decoded_file = csv_file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded_file))
            
            created = 0
            updated = 0
            errors = []
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    number = row.get('number', '').strip()
                    if not number:
                        continue
                    
                    data = {
                        'number': number,
                        'type': row.get('type', 'mobile').strip() or 'mobile',
                        'status': row.get('status', 'active').strip() or 'active',
                        'country_code': row.get('country_code', '').strip(),
                        'description': row.get('description', '').strip(),
                    }
                    
                    provider_name = row.get('provider', '').strip()
                    if provider_name:
                        provider, _ = models.TelephonyProvider.objects.get_or_create(  # Изменено
                            name=provider_name
                        )
                        data['provider'] = provider
                    
                    temp_phone = models.PhoneNumber(**data)
                    temp_phone.clean()
                    
                    existing = models.PhoneNumber.objects.filter(
                        normalized_number=temp_phone.normalized_number
                    ).first()
                    
                    if existing and update_existing:
                        for key, value in data.items():
                            setattr(existing, key, value)
                        existing.clean()
                        existing.save()
                        updated += 1
                    elif not existing:
                        phone = models.PhoneNumber(**data)
                        phone.clean()
                        phone.save()
                        created += 1
                    else:
                        errors.append(f"Row {row_num}: Number {number} already exists")
                        
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            if created or updated:
                messages.success(
                    self.request,
                    f'Import completed: {created} created, {updated} updated'
                )
            
            if errors:
                for error in errors[:10]:
                    messages.warning(self.request, error)
                
                if len(errors) > 10:
                    messages.warning(
                        self.request,
                        f'... and {len(errors) - 10} more errors'
                    )
            
            return redirect('plugins:netbox_phonebox:phonenumber_list')
            
        except Exception as e:
            messages.error(
                self.request,
                f'Failed to import CSV: {str(e)}'
            )
            return self.form_invalid(form)


class PhoneNumberBulkImportView(LoginRequiredMixin, FormView):
    """Bulk import phone numbers from text"""
    
    template_name = 'netbox_phonebox/phonenumber_bulk_import.html'
    form_class = forms.PhoneNumberBulkImportForm
    
    def form_valid(self, form):
        numbers_text = form.cleaned_data['numbers']
        country_code = form.cleaned_data.get('country_code', '')
        phone_type = form.cleaned_data['type']
        status = form.cleaned_data['status']
        provider = form.cleaned_data.get('provider')
        
        numbers = [n.strip() for n in numbers_text.split('\n') if n.strip()]
        
        created = 0
        errors = []
        
        for number in numbers:
            try:
                phone = models.PhoneNumber(
                    number=number,
                    country_code=country_code,
                    type=phone_type,
                    status=status,
                    provider=provider
                )
                phone.clean()
                phone.save()
                created += 1
            except Exception as e:
                errors.append(f"{number}: {str(e)}")
        
        if created:
            messages.success(
                self.request,
                f'Successfully imported {created} phone numbers'
            )
        
        if errors:
            for error in errors[:10]:
                messages.warning(self.request, error)
            
            if len(errors) > 10:
                messages.warning(
                    self.request,
                    f'... and {len(errors) - 10} more errors'
                )
        
        return redirect('plugins:netbox_phonebox:phonenumber_list')


class PhoneNumberExportView(LoginRequiredMixin, View):
    """Export phone numbers to CSV"""
    
    def get(self, request):
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            'ID',
            'Number',
            'Normalized Number',
            'Country Code',
            'Type',
            'Status',
            'Provider',
            'Contact',
            'Device',
            'Virtual Machine',
            'Description',
            'Carrier',
            'Location',
            'Created',
        ])
        
        for phone in models.PhoneNumber.objects.all().select_related(
            'provider', 'contact', 'device', 'virtual_machine'
        ):
            writer.writerow([
                phone.pk,
                phone.formatted_international,
                phone.normalized_number,
                phone.country_code,
                phone.get_type_display(),
                phone.get_status_display(),
                phone.provider.name if phone.provider else '',
                str(phone.contact) if phone.contact else '',
                str(phone.device) if phone.device else '',
                str(phone.virtual_machine) if phone.virtual_machine else '',
                phone.description,
                phone.carrier_name,
                phone.geocoding_description,
                phone.created.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        
        response = HttpResponse(
            output.getvalue(),
            content_type='text/csv'
        )
        response['Content-Disposition'] = 'attachment; filename="phone_numbers.csv"'
        
        return response


class TelephonyProviderListView(generic.ObjectListView):  # Изменено
    """List view for telephony providers"""
    queryset = models.TelephonyProvider.objects.all()  # Изменено
    table = tables.TelephonyProviderTable  # Изменено
    filterset = filtersets.TelephonyProviderFilterSet  # Изменено
    filterset_form = forms.TelephonyProviderFilterForm  # Изменено


class TelephonyProviderView(generic.ObjectView):
    """Detail view for telephony provider"""
    queryset = models.TelephonyProvider.objects.all()
    
    def get_extra_context(self, request, instance):
        """Add statistics to context"""
        stats = {
            'total': instance.phone_numbers.count(),
            'active': instance.phone_numbers.filter(status='active').count(),
            'reserved': instance.phone_numbers.filter(status='reserved').count(),
            'deprecated': instance.phone_numbers.filter(status='deprecated').count(),
        }
        
        return {
            'stats': stats,
        }


class TelephonyProviderEditView(generic.ObjectEditView):  # Изменено
    """Edit view for telephony provider"""
    queryset = models.TelephonyProvider.objects.all()  # Изменено
    form = forms.TelephonyProviderForm  # Изменено


class TelephonyProviderDeleteView(generic.ObjectDeleteView):  # Изменено
    """Delete view for telephony provider"""
    queryset = models.TelephonyProvider.objects.all()  # Изменено


class TelephonyProviderBulkDeleteView(generic.BulkDeleteView):  # Изменено
    """Bulk delete view for telephony providers"""
    queryset = models.TelephonyProvider.objects.all()  # Изменено
    table = tables.TelephonyProviderTable  # Изменено
    
class PBXServerListView(generic.ObjectListView):
    """List view for PBX servers"""
    queryset = models.PBXServer.objects.all()
    table = tables.PBXServerTable
    filterset = filtersets.PBXServerFilterSet
    filterset_form = forms.PBXServerFilterForm


class PBXServerView(generic.ObjectView):
    """Detail view for PBX server"""
    queryset = models.PBXServer.objects.all()
    
    def get_extra_context(self, request, instance):
        """Add statistics to context"""
        from django.utils import timezone  # Можно добавить здесь для уверенности
        
        stats = {
            'extensions': instance.extensions.count(),
            'active_extensions': instance.extensions.filter(enabled=True).count(),
            'trunks': instance.sip_trunks.count(),
            'active_trunks': instance.sip_trunks.filter(enabled=True).count(),
            'total_calls': instance.call_logs.count(),
            'calls_today': instance.call_logs.filter(
                start_time__date=timezone.now().date()
            ).count(),
        }
        
        # Get PBX status
        status = get_pbx_status(instance)
        
        return {
            'stats': stats,
            'pbx_status': status,
        }

class PBXServerEditView(generic.ObjectEditView):
    """Edit view for PBX server"""
    queryset = models.PBXServer.objects.all()
    form = forms.PBXServerForm


class PBXServerDeleteView(generic.ObjectDeleteView):
    """Delete view for PBX server"""
    queryset = models.PBXServer.objects.all()


class PBXServerBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for PBX servers"""
    queryset = models.PBXServer.objects.all()
    table = tables.PBXServerTable


# SIP Trunk Views

class SIPTrunkListView(generic.ObjectListView):
    """List view for SIP trunks"""
    queryset = models.SIPTrunk.objects.all()
    table = tables.SIPTrunkTable
    filterset = filtersets.SIPTrunkFilterSet
    filterset_form = forms.SIPTrunkFilterForm


class SIPTrunkView(generic.ObjectView):
    """Detail view for SIP trunk"""
    queryset = models.SIPTrunk.objects.all()


class SIPTrunkEditView(generic.ObjectEditView):
    """Edit view for SIP trunk"""
    queryset = models.SIPTrunk.objects.all()
    form = forms.SIPTrunkForm


class SIPTrunkDeleteView(generic.ObjectDeleteView):
    """Delete view for SIP trunk"""
    queryset = models.SIPTrunk.objects.all()


class SIPTrunkBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for SIP trunks"""
    queryset = models.SIPTrunk.objects.all()
    table = tables.SIPTrunkTable


# Extension Views

class ExtensionListView(generic.ObjectListView):
    """List view for extensions"""
    queryset = models.Extension.objects.all()
    table = tables.ExtensionTable
    filterset = filtersets.ExtensionFilterSet
    filterset_form = forms.ExtensionFilterForm


class ExtensionView(generic.ObjectView):
    """Detail view for extension"""
    queryset = models.Extension.objects.all()
    
    def get_extra_context(self, request, instance):
        """Add call statistics to context"""
        stats = {
            'phone_numbers': instance.phone_numbers.count(),
            'total_calls': instance.call_logs.count(),
            'inbound_calls': instance.call_logs.filter(direction='inbound').count(),
            'outbound_calls': instance.call_logs.filter(direction='outbound').count(),
            'answered_calls': instance.call_logs.filter(status='answered').count(),
        }
        
        # Recent calls
        recent_calls = instance.call_logs.order_by('-start_time')[:10]
        
        return {
            'stats': stats,
            'recent_calls': recent_calls,
        }


class ExtensionEditView(generic.ObjectEditView):
    """Edit view for extension"""
    queryset = models.Extension.objects.all()
    form = forms.ExtensionForm


class ExtensionDeleteView(generic.ObjectDeleteView):
    """Delete view for extension"""
    queryset = models.Extension.objects.all()


class ExtensionBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for extensions"""
    queryset = models.Extension.objects.all()
    table = tables.ExtensionTable


# Call Log Views

class CallLogListView(generic.ObjectListView):
    """List view for call logs"""
    queryset = models.CallLog.objects.all()
    table = tables.CallLogTable
    filterset = filtersets.CallLogFilterSet
    filterset_form = forms.CallLogFilterForm


class CallLogView(generic.ObjectView):
    """Detail view for call log"""
    queryset = models.CallLog.objects.all()


class CallLogDeleteView(generic.ObjectDeleteView):
    """Delete view for call log"""
    queryset = models.CallLog.objects.all()


class CallLogBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for call logs"""
    queryset = models.CallLog.objects.all()
    table = tables.CallLogTable


# Make Call View

class MakeCallView(LoginRequiredMixin, FormView):
    """View for initiating calls"""
    
    template_name = 'netbox_phonebox/make_call.html'
    form_class = forms.MakeCallForm
    
    def get_initial(self):
        """Pre-fill form from query parameters"""
        initial = super().get_initial()
        
        if 'extension' in self.request.GET:
            try:
                extension_id = int(self.request.GET['extension'])
                extension = models.Extension.objects.get(pk=extension_id)
                initial['extension'] = extension
                initial['pbx_server'] = extension.pbx_server
            except:
                pass
        
        if 'number' in self.request.GET:
            initial['to_number'] = self.request.GET['number']
        
        return initial
    
    def form_valid(self, form):
        """Initiate the call"""
        pbx_server = form.cleaned_data['pbx_server']
        extension = form.cleaned_data['extension']
        to_number = form.cleaned_data['to_number']
        
        # Make the call
        result = make_call(pbx_server, extension, to_number)
        
        if result['success']:
            messages.success(
                self.request,
                f"Call initiated from {extension.extension} to {to_number}"
            )
        else:
            messages.error(
                self.request,
                f"Failed to initiate call: {result['message']}"
            )
        
        return redirect('plugins:netbox_phonebox:extension', pk=extension.pk)


# Call Statistics View

class CallStatisticsView(LoginRequiredMixin, TemplateView):
    """View for call statistics and analytics"""
    
    template_name = 'netbox_phonebox/call_statistics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Overall statistics
        total_calls = models.CallLog.objects.count()
        answered_calls = models.CallLog.objects.filter(status='answered').count()
        
        # Calculate answer rate
        answer_rate = (answered_calls / total_calls * 100) if total_calls > 0 else 0
        
        # Calls by direction
        inbound = models.CallLog.objects.filter(direction='inbound').count()
        outbound = models.CallLog.objects.filter(direction='outbound').count()
        internal = models.CallLog.objects.filter(direction='internal').count()
        
        # Calls by status
        status_stats = models.CallLog.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Top extensions by call count
        top_extensions = models.Extension.objects.annotate(
            call_count=Count('call_logs')
        ).order_by('-call_count')[:10]
        
        # Recent calls
        recent_calls = models.CallLog.objects.order_by('-start_time')[:20]
        
        # Total call duration
        total_duration = models.CallLog.objects.filter(
            status='answered'
        ).aggregate(Sum('duration'))['duration__sum'] or 0
        
        context.update({
            'total_calls': total_calls,
            'answered_calls': answered_calls,
            'answer_rate': round(answer_rate, 2),
            'inbound': inbound,
            'outbound': outbound,
            'internal': internal,
            'status_stats': status_stats,
            'top_extensions': top_extensions,
            'recent_calls': recent_calls,
            'total_duration': total_duration,
        })
        
        return context