from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import FormView, View
from django.http import HttpResponse
import csv
import io


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
            
            for row_num, row in enumerate(reader, start=2):  # start=2 т.к. строка 1 - заголовки
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
                    temp_phone.clean()  # Это нормализует номер
                    
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
                        errors.append(f"Row {row_num}: Number {number} already exists (use update mode to update)")
                        
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            # Сообщения о результатах
            if created or updated:
                messages.success(
                    self.request,
                    f'Import completed: {created} created, {updated} updated'
                )
            
            if errors:
                for error in errors[:10]:  # Показываем первые 10 ошибок
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