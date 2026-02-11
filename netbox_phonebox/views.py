from netbox.views import generic
from django.db.models import Count
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import TemplateView, FormView, View
from django.http import HttpResponse
from . import filtersets, forms, models, tables
import csv
import io


class PhoneNumberDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard with phone number statistics"""
    
    template_name = 'netbox_phonebox/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Общая статистика
        total = models.PhoneNumber.objects.count()
        active = models.PhoneNumber.objects.filter(status='active').count()
        reserved = models.PhoneNumber.objects.filter(status='reserved').count()
        deprecated = models.PhoneNumber.objects.filter(status='deprecated').count()
        
        # Статистика по типам
        type_stats = models.PhoneNumber.objects.values('type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Статистика по провайдерам
        provider_stats = models.PhoneNumber.objects.filter(
            provider__isnull=False
        ).values(
            'provider__name', 'provider__id'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Статистика по странам
        country_stats = models.PhoneNumber.objects.exclude(
            country_code=''
        ).values('country_code').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Неназначенные номера
        unassigned = models.PhoneNumber.objects.filter(
            contact__isnull=True,
            device__isnull=True,
            virtual_machine__isnull=True
        ).count()
        
        # Недавно добавленные
        recent_numbers = models.PhoneNumber.objects.order_by('-created')[:10]
        
        # Статистика провайдеров
        providers_count = models.Provider.objects.count()
        
        # Номера по провайдерам (для графика)
        provider_chart_data = []
        provider_chart_labels = []
        for stat in provider_stats:
            provider_chart_labels.append(stat['provider__name'])
            provider_chart_data.append(stat['count'])
        
        # Номера по типам (для графика)
        type_chart_data = []
        type_chart_labels = []
        for stat in type_stats:
            type_chart_labels.append(dict(models.PhoneNumber.TYPE_CHOICES).get(stat['type'], stat['type']))
            type_chart_data.append(stat['count'])
        
        context.update({
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
            # Читаем CSV
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
                    
                    # Подготовка данных
                    data = {
                        'number': number,
                        'type': row.get('type', 'mobile').strip() or 'mobile',
                        'status': row.get('status', 'active').strip() or 'active',
                        'country_code': row.get('country_code', '').strip(),
                        'description': row.get('description', '').strip(),
                    }
                    
                    # Провайдер
                    provider_name = row.get('provider', '').strip()
                    if provider_name:
                        provider, _ = models.Provider.objects.get_or_create(
                            name=provider_name
                        )
                        data['provider'] = provider
                    
                    # Создаем временный объект для валидации и нормализации
                    temp_phone = models.PhoneNumber(**data)
                    temp_phone.clean()
                    
                    # Проверяем существование по нормализованному номеру
                    existing = models.PhoneNumber.objects.filter(
                        normalized_number=temp_phone.normalized_number
                    ).first()
                    
                    if existing and update_existing:
                        # Обновляем существующий
                        for key, value in data.items():
                            setattr(existing, key, value)
                        existing.clean()
                        existing.save()
                        updated += 1
                    elif not existing:
                        # Создаем новый
                        phone = models.PhoneNumber(**data)
                        phone.clean()
                        phone.save()
                        created += 1
                    else:
                        errors.append(f"Row {row_num}: Number {number} already exists")
                        
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            # Сообщения о результатах
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
        # Создаем CSV в памяти
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Заголовки
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
        
        # Данные
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
        
        # Подготовка ответа
        response = HttpResponse(
            output.getvalue(),
            content_type='text/csv'
        )
        response['Content-Disposition'] = 'attachment; filename="phone_numbers.csv"'
        
        return response


class ProviderListView(generic.ObjectListView):
    """List view for providers"""
    queryset = models.Provider.objects.all()
    table = tables.ProviderTable
    filterset = filtersets.ProviderFilterSet
    filterset_form = forms.ProviderFilterForm


class ProviderView(generic.ObjectView):
    """Detail view for provider"""
    queryset = models.Provider.objects.all()


class ProviderEditView(generic.ObjectEditView):
    """Edit view for provider"""
    queryset = models.Provider.objects.all()
    form = forms.ProviderForm


class ProviderDeleteView(generic.ObjectDeleteView):
    """Delete view for provider"""
    queryset = models.Provider.objects.all()


class ProviderBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for providers"""
    queryset = models.Provider.objects.all()
    table = tables.ProviderTable