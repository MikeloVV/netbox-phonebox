from django.urls import path
from netbox.views.generic import ObjectChangeLogView
from . import views
from .models import (
    PhoneNumber, TelephonyProvider, PBXServer,
    SIPTrunk, Extension, CallLog
)

urlpatterns = [
    # Dashboard
    path('', views.PhoneNumberDashboardView.as_view(), name='dashboard'),
    
    # Phone Numbers
    path('phone-numbers/', views.PhoneNumberListView.as_view(), name='phonenumber_list'),
    path('phone-numbers/add/', views.PhoneNumberEditView.as_view(), name='phonenumber_add'),
    path('phone-numbers/import/', views.PhoneNumberBulkImportView.as_view(), name='phonenumber_import'),
    path('phone-numbers/edit/', views.PhoneNumberBulkEditView.as_view(), name='phonenumber_bulk_edit'),
    path('phone-numbers/delete/', views.PhoneNumberBulkDeleteView.as_view(), name='phonenumber_bulk_delete'),
    path('phone-numbers/<int:pk>/', views.PhoneNumberView.as_view(), name='phonenumber'),
    path('phone-numbers/<int:pk>/edit/', views.PhoneNumberEditView.as_view(), name='phonenumber_edit'),
    path('phone-numbers/<int:pk>/delete/', views.PhoneNumberDeleteView.as_view(), name='phonenumber_delete'),
    path('phone-numbers/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='phonenumber_changelog', kwargs={'model': PhoneNumber}),
    
    # Telephony Providers
    path('providers/', views.TelephonyProviderListView.as_view(), name='telephonyprovider_list'),
    path('providers/add/', views.TelephonyProviderEditView.as_view(), name='telephonyprovider_add'),
    path('providers/import/', views.TelephonyProviderBulkImportView.as_view(), name='telephonyprovider_import'),
    path('providers/edit/', views.TelephonyProviderBulkEditView.as_view(), name='telephonyprovider_bulk_edit'),
    path('providers/delete/', views.TelephonyProviderBulkDeleteView.as_view(), name='telephonyprovider_bulk_delete'),
    path('providers/<int:pk>/', views.TelephonyProviderView.as_view(), name='telephonyprovider'),
    path('providers/<int:pk>/edit/', views.TelephonyProviderEditView.as_view(), name='telephonyprovider_edit'),
    path('providers/<int:pk>/delete/', views.TelephonyProviderDeleteView.as_view(), name='telephonyprovider_delete'),
    path('providers/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='telephonyprovider_changelog', kwargs={'model': TelephonyProvider}),
    
    # PBX Servers
    path('pbx-servers/', views.PBXServerListView.as_view(), name='pbxserver_list'),
    path('pbx-servers/add/', views.PBXServerEditView.as_view(), name='pbxserver_add'),
    path('pbx-servers/import/', views.PBXServerBulkImportView.as_view(), name='pbxserver_import'),
    path('pbx-servers/edit/', views.PBXServerBulkEditView.as_view(), name='pbxserver_bulk_edit'),
    path('pbx-servers/delete/', views.PBXServerBulkDeleteView.as_view(), name='pbxserver_bulk_delete'),
    path('pbx-servers/<int:pk>/', views.PBXServerView.as_view(), name='pbxserver'),
    path('pbx-servers/<int:pk>/edit/', views.PBXServerEditView.as_view(), name='pbxserver_edit'),
    path('pbx-servers/<int:pk>/delete/', views.PBXServerDeleteView.as_view(), name='pbxserver_delete'),
    path('pbx-servers/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='pbxserver_changelog', kwargs={'model': PBXServer}),
    
    # SIP Trunks
    path('sip-trunks/', views.SIPTrunkListView.as_view(), name='siptrunk_list'),
    path('sip-trunks/add/', views.SIPTrunkEditView.as_view(), name='siptrunk_add'),
    path('sip-trunks/import/', views.SIPTrunkBulkImportView.as_view(), name='siptrunk_import'),
    path('sip-trunks/edit/', views.SIPTrunkBulkEditView.as_view(), name='siptrunk_bulk_edit'),
    path('sip-trunks/delete/', views.SIPTrunkBulkDeleteView.as_view(), name='siptrunk_bulk_delete'),
    path('sip-trunks/<int:pk>/', views.SIPTrunkView.as_view(), name='siptrunk'),
    path('sip-trunks/<int:pk>/edit/', views.SIPTrunkEditView.as_view(), name='siptrunk_edit'),
    path('sip-trunks/<int:pk>/delete/', views.SIPTrunkDeleteView.as_view(), name='siptrunk_delete'),
    path('sip-trunks/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='siptrunk_changelog', kwargs={'model': SIPTrunk}),
    
    # Extensions
    path('extensions/', views.ExtensionListView.as_view(), name='extension_list'),
    path('extensions/add/', views.ExtensionEditView.as_view(), name='extension_add'),
    path('extensions/import/', views.ExtensionBulkImportView.as_view(), name='extension_import'),
    path('extensions/edit/', views.ExtensionBulkEditView.as_view(), name='extension_bulk_edit'),
    path('extensions/delete/', views.ExtensionBulkDeleteView.as_view(), name='extension_bulk_delete'),
    path('extensions/<int:pk>/', views.ExtensionView.as_view(), name='extension'),
    path('extensions/<int:pk>/edit/', views.ExtensionEditView.as_view(), name='extension_edit'),
    path('extensions/<int:pk>/delete/', views.ExtensionDeleteView.as_view(), name='extension_delete'),
    path('extensions/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='extension_changelog', kwargs={'model': Extension}),
    
    # Call Logs
    path('call-logs/', views.CallLogListView.as_view(), name='calllog_list'),
    path('call-logs/<int:pk>/', views.CallLogView.as_view(), name='calllog'),
    path('call-logs/<int:pk>/delete/', views.CallLogDeleteView.as_view(), name='calllog_delete'),
    path('call-logs/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='calllog_changelog', kwargs={'model': CallLog}),
    path('call-logs/delete/', views.CallLogBulkDeleteView.as_view(), name='calllog_bulk_delete'),
    
    # Call Statistics
    path('call-statistics/', views.CallStatisticsView.as_view(), name='call_statistics'),
    
    # Make Call
    path('make-call/', views.MakeCallView.as_view(), name='make_call'),
]