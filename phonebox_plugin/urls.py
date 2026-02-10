from django.urls import path
from netbox.views.generic import ObjectChangeLogView
from . import views
from .models import PhoneNumber, Provider

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
    
    # Providers
    path('providers/', views.ProviderListView.as_view(), name='provider_list'),
    path('providers/add/', views.ProviderEditView.as_view(), name='provider_add'),
    path('providers/<int:pk>/', views.ProviderView.as_view(), name='provider'),
    path('providers/<int:pk>/edit/', views.ProviderEditView.as_view(), name='provider_edit'),
    path('providers/<int:pk>/delete/', views.ProviderDeleteView.as_view(), name='provider_delete'),
    path('providers/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='provider_changelog', kwargs={'model': Provider}),
    path('providers/delete/', views.ProviderBulkDeleteView.as_view(), name='provider_bulk_delete'),
]