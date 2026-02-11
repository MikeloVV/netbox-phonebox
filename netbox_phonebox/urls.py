from django.urls import path
from netbox.views.generic import ObjectChangeLogView
from . import views
from .models import PhoneNumber, TelephonyProvider  # Изменено

urlpatterns = [
    # Dashboard
    path('', views.PhoneNumberDashboardView.as_view(), name='phonenumber_dashboard'),
    
    # Phone Numbers
    path('phone-numbers/', views.PhoneNumberListView.as_view(), name='phonenumber_list'),
    path('phone-numbers/add/', views.PhoneNumberEditView.as_view(), name='phonenumber_add'),
    path('phone-numbers/<int:pk>/', views.PhoneNumberView.as_view(), name='phonenumber'),
    path('phone-numbers/<int:pk>/edit/', views.PhoneNumberEditView.as_view(), name='phonenumber_edit'),
    path('phone-numbers/<int:pk>/delete/', views.PhoneNumberDeleteView.as_view(), name='phonenumber_delete'),
    path('phone-numbers/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='phonenumber_changelog', kwargs={'model': PhoneNumber}),
    path('phone-numbers/delete/', views.PhoneNumberBulkDeleteView.as_view(), name='phonenumber_bulk_delete'),
    
    # Import/Export
    path('phone-numbers/import/', views.PhoneNumberImportView.as_view(), name='phonenumber_import'),
    path('phone-numbers/bulk-import/', views.PhoneNumberBulkImportView.as_view(), name='phonenumber_bulk_import'),
    path('phone-numbers/export/', views.PhoneNumberExportView.as_view(), name='phonenumber_export'),
    
    # Telephony Providers - Изменено
    path('providers/', views.TelephonyProviderListView.as_view(), name='telephonyprovider_list'),
    path('providers/add/', views.TelephonyProviderEditView.as_view(), name='telephonyprovider_add'),
    path('providers/<int:pk>/', views.TelephonyProviderView.as_view(), name='telephonyprovider'),
    path('providers/<int:pk>/edit/', views.TelephonyProviderEditView.as_view(), name='telephonyprovider_edit'),
    path('providers/<int:pk>/delete/', views.TelephonyProviderDeleteView.as_view(), name='telephonyprovider_delete'),
    path('providers/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='telephonyprovider_changelog', kwargs={'model': TelephonyProvider}),
    path('providers/delete/', views.TelephonyProviderBulkDeleteView.as_view(), name='telephonyprovider_bulk_delete'),
]