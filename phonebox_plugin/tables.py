import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from django.utils.html import format_html
from .models import PhoneNumber, Provider


class PhoneNumberTable(NetBoxTable):
    """Table for displaying phone numbers"""
    
    number = tables.Column(
        linkify=True,
        verbose_name='Number'
    )
    
    formatted_number = tables.TemplateColumn(
        template_code='''
        <strong>{{ record.formatted_international }}</strong><br>
        <small class="text-muted">{{ record.normalized_number }}</small>
        ''',
        verbose_name='Formatted',
        orderable=False
    )
    
    country = tables.TemplateColumn(
        template_code='''
        {% if record.country_code %}
            <span class="fi fi-{{ record.country_code|lower }}"></span>
            {{ record.country_code }}
        {% else %}
            <span class="text-muted">—</span>
        {% endif %}
        ''',
        verbose_name='Country',
        orderable=False
    )
    
    type = tables.Column(
        verbose_name='Type'
    )
    
    status = tables.TemplateColumn(
        template_code='''
        {% if record.status == 'active' %}
            <span class="badge bg-success">{{ record.get_status_display }}</span>
        {% elif record.status == 'reserved' %}
            <span class="badge bg-warning">{{ record.get_status_display }}</span>
        {% else %}
            <span class="badge bg-danger">{{ record.get_status_display }}</span>
        {% endif %}
        ''',
        verbose_name='Status'
    )
    
    provider = tables.Column(
        linkify=True,
        verbose_name='Provider'
    )
    
    contact = tables.Column(
        linkify=True,
        verbose_name='Contact'
    )
    
    device = tables.Column(
        linkify=True,
        verbose_name='Device'
    )
    
    virtual_machine = tables.Column(
        linkify=True,
        verbose_name='VM'
    )
    
    assigned_to = tables.TemplateColumn(
        template_code='''
        {% if record.contact %}
            <i class="mdi mdi-account"></i> <a href="{{ record.contact.get_absolute_url }}">{{ record.contact }}</a>
        {% elif record.device %}
            <i class="mdi mdi-server"></i> <a href="{{ record.device.get_absolute_url }}">{{ record.device }}</a>
        {% elif record.virtual_machine %}
            <i class="mdi mdi-monitor"></i> <a href="{{ record.virtual_machine.get_absolute_url }}">{{ record.virtual_machine }}</a>
        {% else %}
            <span class="text-muted">Unassigned</span>
        {% endif %}
        ''',
        verbose_name='Assigned To',
        orderable=False
    )
    
    call_button = tables.TemplateColumn(
        template_code='''
        <a href="{{ record.click_to_call_url }}" 
           class="btn btn-sm btn-success" 
           title="Call">
            <i class="mdi mdi-phone"></i>
        </a>
        ''',
        verbose_name='',
        orderable=False
    )
    
    tags = columns.TagColumn(
        url_name='plugins:netbox_phonebox:phonenumber_list'
    )
    
    class Meta(NetBoxTable.Meta):
        model = PhoneNumber
        fields = (
            'pk', 'number', 'formatted_number', 'country', 'type', 'status',
            'provider', 'assigned_to', 'description', 'call_button',
            'tags', 'created', 'last_updated', 'actions'
        )
        default_columns = (
            'pk', 'formatted_number', 'country', 'type', 'status',
            'provider', 'assigned_to', 'call_button'
        )


class ProviderTable(NetBoxTable):
    """Table for displaying providers"""
    
    name = tables.Column(
        linkify=True,
        verbose_name='Name'
    )
    
    numbers_count = tables.TemplateColumn(
        template_code='''
        <span class="badge bg-primary">{{ record.numbers_count }}</span>
        ''',
        verbose_name='Numbers',
        orderable=False
    )
    
    website = tables.TemplateColumn(
        template_code='''
        {% if record.website %}
            <a href="{{ record.website }}" target="_blank">
                <i class="mdi mdi-open-in-new"></i> Website
            </a>
        {% else %}
            <span class="text-muted">—</span>
        {% endif %}
        ''',
        verbose_name='Website',
        orderable=False
    )
    
    support_phone = tables.Column(
        verbose_name='Support Phone'
    )
    
    support_email = tables.Column(
        verbose_name='Support Email'
    )
    
    tags = columns.TagColumn(
        url_name='plugins:netbox_phonebox:provider_list'
    )
    
    class Meta(NetBoxTable.Meta):
        model = Provider
        fields = (
            'pk', 'name', 'description', 'numbers_count', 'website',
            'support_phone', 'support_email', 'tags', 'created',
            'last_updated', 'actions'
        )
        default_columns = (
            'pk', 'name', 'description', 'numbers_count', 'website',
            'support_phone'
        )