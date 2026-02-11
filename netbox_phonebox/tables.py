import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from .models import (
    PhoneNumber, TelephonyProvider, PBXServer, 
    SIPTrunk, Extension, CallLog
)


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


class TelephonyProviderTable(NetBoxTable):  # Изменено
    """Table for displaying telephony providers"""
    
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
        url_name='plugins:netbox_phonebox:telephonyprovider_list'  # Изменено
    )
    
    class Meta(NetBoxTable.Meta):
        model = TelephonyProvider  # Изменено
        fields = (
            'pk', 'name', 'description', 'numbers_count', 'website',
            'support_phone', 'support_email', 'tags', 'created',
            'last_updated', 'actions'
        )
        default_columns = (
            'pk', 'name', 'description', 'numbers_count', 'website',
            'support_phone'
        )
        
class PBXServerTable(NetBoxTable):
    """Table for displaying PBX servers"""
    
    name = tables.Column(
        linkify=True,
        verbose_name='Name'
    )
    
    type = tables.Column(
        verbose_name='Type'
    )
    
    connection = tables.TemplateColumn(
        template_code='''
        <code>{{ record.hostname }}:{{ record.ami_port }}</code>
        ''',
        verbose_name='Connection',
        orderable=False
    )
    
    web_url = tables.TemplateColumn(
        template_code='''
        {% if record.web_url %}
            <a href="{{ record.web_url }}" target="_blank">
                <i class="mdi mdi-open-in-new"></i> Web UI
            </a>
        {% else %}
            <span class="text-muted">—</span>
        {% endif %}
        ''',
        verbose_name='Web Interface',
        orderable=False
    )
    
    enabled = tables.BooleanColumn(
        verbose_name='Enabled'
    )
    
    extensions_count = tables.TemplateColumn(
        template_code='''
        <span class="badge bg-info">{{ record.extensions.count }}</span>
        ''',
        verbose_name='Extensions',
        orderable=False
    )
    
    trunks_count = tables.TemplateColumn(
        template_code='''
        <span class="badge bg-primary">{{ record.sip_trunks.count }}</span>
        ''',
        verbose_name='Trunks',
        orderable=False
    )
    
    tags = columns.TagColumn(
        url_name='plugins:netbox_phonebox:pbxserver_list'
    )
    
    class Meta(NetBoxTable.Meta):
        model = PBXServer
        fields = (
            'pk', 'name', 'type', 'connection', 'web_url', 'enabled',
            'extensions_count', 'trunks_count', 'description',
            'tags', 'created', 'last_updated', 'actions'
        )
        default_columns = (
            'pk', 'name', 'type', 'connection', 'enabled',
            'extensions_count', 'trunks_count'
        )


class SIPTrunkTable(NetBoxTable):
    """Table for displaying SIP trunks"""
    
    name = tables.Column(
        linkify=True,
        verbose_name='Name'
    )
    
    pbx_server = tables.Column(
        linkify=True,
        verbose_name='PBX Server'
    )
    
    provider = tables.Column(
        linkify=True,
        verbose_name='Provider'
    )
    
    type = tables.Column(
        verbose_name='Type'
    )
    
    connection = tables.TemplateColumn(
        template_code='''
        <code>{{ record.host }}:{{ record.port }}</code><br>
        <small class="text-muted">{{ record.get_transport_display }}</small>
        ''',
        verbose_name='Connection',
        orderable=False
    )
    
    enabled = tables.BooleanColumn(
        verbose_name='Enabled'
    )
    
    tags = columns.TagColumn(
        url_name='plugins:netbox_phonebox:siptrunk_list'
    )
    
    class Meta(NetBoxTable.Meta):
        model = SIPTrunk
        fields = (
            'pk', 'name', 'pbx_server', 'provider', 'type', 'connection',
            'enabled', 'description', 'tags', 'created', 'last_updated', 'actions'
        )
        default_columns = (
            'pk', 'name', 'pbx_server', 'provider', 'type', 'connection', 'enabled'
        )


class ExtensionTable(NetBoxTable):
    """Table for displaying extensions"""
    
    extension = tables.Column(
        linkify=True,
        verbose_name='Extension'
    )
    
    pbx_server = tables.Column(
        linkify=True,
        verbose_name='PBX Server'
    )
    
    type = tables.Column(
        verbose_name='Type'
    )
    
    assigned_to = tables.TemplateColumn(
        template_code='''
        {% if record.contact %}
            <i class="mdi mdi-account"></i> <a href="{{ record.contact.get_absolute_url }}">{{ record.contact }}</a>
        {% elif record.device %}
            <i class="mdi mdi-phone-classic"></i> <a href="{{ record.device.get_absolute_url }}">{{ record.device }}</a>
        {% else %}
            <span class="text-muted">Unassigned</span>
        {% endif %}
        ''',
        verbose_name='Assigned To',
        orderable=False
    )
    
    phone_numbers = tables.TemplateColumn(
        template_code='''
        {% if record.phone_numbers.exists %}
            <span class="badge bg-success">{{ record.phone_numbers.count }}</span>
        {% else %}
            <span class="text-muted">—</span>
        {% endif %}
        ''',
        verbose_name='Phone Numbers',
        orderable=False
    )
    
    enabled = tables.BooleanColumn(
        verbose_name='Enabled'
    )
    
    call_button = tables.TemplateColumn(
        template_code='''
        <a href="{% url 'plugins:netbox_phonebox:make_call' %}?extension={{ record.pk }}" 
           class="btn btn-sm btn-success" 
           title="Make Call">
            <i class="mdi mdi-phone"></i>
        </a>
        ''',
        verbose_name='',
        orderable=False
    )
    
    tags = columns.TagColumn(
        url_name='plugins:netbox_phonebox:extension_list'
    )
    
    class Meta(NetBoxTable.Meta):
        model = Extension
        fields = (
            'pk', 'extension', 'pbx_server', 'type', 'assigned_to',
            'phone_numbers', 'enabled', 'call_button', 'description',
            'tags', 'created', 'last_updated', 'actions'
        )
        default_columns = (
            'pk', 'extension', 'pbx_server', 'type', 'assigned_to',
            'phone_numbers', 'enabled', 'call_button'
        )


class CallLogTable(NetBoxTable):
    """Table for displaying call logs"""
    
    call_id = tables.Column(
        linkify=True,
        verbose_name='Call ID'
    )
    
    direction = tables.TemplateColumn(
        template_code='''
        {% if record.direction == 'inbound' %}
            <span class="badge bg-success"><i class="mdi mdi-phone-incoming"></i> Inbound</span>
        {% elif record.direction == 'outbound' %}
            <span class="badge bg-primary"><i class="mdi mdi-phone-outgoing"></i> Outbound</span>
        {% else %}
            <span class="badge bg-info"><i class="mdi mdi-phone-in-talk"></i> Internal</span>
        {% endif %}
        ''',
        verbose_name='Direction',
        orderable=False
    )
    
    caller_number = tables.Column(
        verbose_name='Caller'
    )
    
    called_number = tables.Column(
        verbose_name='Called'
    )
    
    extension = tables.Column(
        linkify=True,
        verbose_name='Extension'
    )
    
    status = tables.TemplateColumn(
        template_code='''
        {% if record.status == 'answered' %}
            <span class="badge bg-success">{{ record.get_status_display }}</span>
        {% elif record.status == 'no_answer' %}
            <span class="badge bg-warning">{{ record.get_status_display }}</span>
        {% elif record.status == 'busy' %}
            <span class="badge bg-danger">{{ record.get_status_display }}</span>
        {% elif record.status == 'failed' %}
            <span class="badge bg-danger">{{ record.get_status_display }}</span>
        {% else %}
            <span class="badge bg-secondary">{{ record.get_status_display }}</span>
        {% endif %}
        ''',
        verbose_name='Status'
    )
    
    start_time = tables.DateTimeColumn(
        verbose_name='Start Time',
        format='Y-m-d H:i:s'
    )
    
    duration = tables.TemplateColumn(
        template_code='''
        {% if record.duration > 0 %}
            {{ record.duration_formatted }}
        {% else %}
            <span class="text-muted">—</span>
        {% endif %}
        ''',
        verbose_name='Duration',
        orderable=False
    )
    
    recording = tables.TemplateColumn(
        template_code='''
        {% if record.recording_url %}
            <a href="{{ record.recording_url }}" target="_blank" class="btn btn-sm btn-outline-primary">
                <i class="mdi mdi-play"></i> Play
            </a>
        {% else %}
            <span class="text-muted">—</span>
        {% endif %}
        ''',
        verbose_name='Recording',
        orderable=False
    )
    
    tags = columns.TagColumn(
        url_name='plugins:netbox_phonebox:calllog_list'
    )
    
    class Meta(NetBoxTable.Meta):
        model = CallLog
        fields = (
            'pk', 'call_id', 'direction', 'caller_number', 'called_number',
            'extension', 'status', 'start_time', 'duration', 'recording',
            'tags', 'created', 'actions'
        )
        default_columns = (
            'pk', 'direction', 'caller_number', 'called_number',
            'extension', 'status', 'start_time', 'duration', 'recording'
        )