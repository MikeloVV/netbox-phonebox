from django.urls import include, path

from netbox.views.generic import ObjectChangeLogView, ObjectJournalView

from . import models, views

urlpatterns = [
    # ──────────────────────────────────────────────
    # PBXServer
    # ──────────────────────────────────────────────
    path("pbx-servers/", views.PBXServerListView.as_view(), name="pbxserver_list"),
    path("pbx-servers/add/", views.PBXServerEditView.as_view(), name="pbxserver_add"),
    path("pbx-servers/import/", views.PBXServerBulkImportView.as_view(), name="pbxserver_import"),
    path("pbx-servers/edit/", views.PBXServerBulkEditView.as_view(), name="pbxserver_bulk_edit"),
    path("pbx-servers/delete/", views.PBXServerBulkDeleteView.as_view(), name="pbxserver_bulk_delete"),
    path("pbx-servers/<int:pk>/", views.PBXServerView.as_view(), name="pbxserver"),
    path("pbx-servers/<int:pk>/edit/", views.PBXServerEditView.as_view(), name="pbxserver_edit"),
    path("pbx-servers/<int:pk>/delete/", views.PBXServerDeleteView.as_view(), name="pbxserver_delete"),
    path(
        "pbx-servers/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="pbxserver_changelog",
        kwargs={"model": models.PBXServer},
    ),
    path(
        "pbx-servers/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="pbxserver_journal",
        kwargs={"model": models.PBXServer},
    ),
    path("pbx-servers/<int:pk>/clone/", views.PBXServerEditView.as_view(), name="pbxserver_clone"),

    # ──────────────────────────────────────────────
    # SIPTrunk
    # ──────────────────────────────────────────────
    path("sip-trunks/", views.SIPTrunkListView.as_view(), name="siptrunk_list"),
    path("sip-trunks/add/", views.SIPTrunkEditView.as_view(), name="siptrunk_add"),
    path("sip-trunks/import/", views.SIPTrunkBulkImportView.as_view(), name="siptrunk_import"),
    path("sip-trunks/edit/", views.SIPTrunkBulkEditView.as_view(), name="siptrunk_bulk_edit"),
    path("sip-trunks/delete/", views.SIPTrunkBulkDeleteView.as_view(), name="siptrunk_bulk_delete"),
    path("sip-trunks/<int:pk>/", views.SIPTrunkView.as_view(), name="siptrunk"),
    path("sip-trunks/<int:pk>/edit/", views.SIPTrunkEditView.as_view(), name="siptrunk_edit"),
    path("sip-trunks/<int:pk>/delete/", views.SIPTrunkDeleteView.as_view(), name="siptrunk_delete"),
    path(
        "sip-trunks/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="siptrunk_changelog",
        kwargs={"model": models.SIPTrunk},
    ),
    path(
        "sip-trunks/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="siptrunk_journal",
        kwargs={"model": models.SIPTrunk},
    ),
    path("sip-trunks/<int:pk>/clone/", views.SIPTrunkEditView.as_view(), name="siptrunk_clone"),

    # ──────────────────────────────────────────────
    # PhoneNumber
    # ──────────────────────────────────────────────
    path("phone-numbers/", views.PhoneNumberListView.as_view(), name="phonenumber_list"),
    path("phone-numbers/add/", views.PhoneNumberEditView.as_view(), name="phonenumber_add"),
    path("phone-numbers/import/", views.PhoneNumberBulkImportView.as_view(), name="phonenumber_import"),
    path("phone-numbers/edit/", views.PhoneNumberBulkEditView.as_view(), name="phonenumber_bulk_edit"),
    path("phone-numbers/delete/", views.PhoneNumberBulkDeleteView.as_view(), name="phonenumber_bulk_delete"),
    path("phone-numbers/<int:pk>/", views.PhoneNumberView.as_view(), name="phonenumber"),
    path("phone-numbers/<int:pk>/edit/", views.PhoneNumberEditView.as_view(), name="phonenumber_edit"),
    path("phone-numbers/<int:pk>/delete/", views.PhoneNumberDeleteView.as_view(), name="phonenumber_delete"),
    path(
        "phone-numbers/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="phonenumber_changelog",
        kwargs={"model": models.PhoneNumber},
    ),
    path(
        "phone-numbers/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="phonenumber_journal",
        kwargs={"model": models.PhoneNumber},
    ),
    path("phone-numbers/<int:pk>/clone/", views.PhoneNumberEditView.as_view(), name="phonenumber_clone"),
]