"""
apps/certificates/urls.py
"""
from django.urls import path
from .views import (
    AdminPanelView, SendCertificateView, 
    VerifyCertificateView, ExportRegistrationsCSVView,
    DashboardView, LinkGeneratorView, BulkSendCertificatesView,
    ResetCertificateStatusView, DeleteRegistrationView,
    ParticipantListView, ExportParticipantsCSVView,
    CheckRegistrationStatusView
)

app_name = "certificates"

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("", AdminPanelView.as_view(), name="panel"),
    path("check-status/", CheckRegistrationStatusView.as_view(), name="check_status"),
    path("participantes/", ParticipantListView.as_view(), name="participants"),
    path("exportar-alunos-csv/", ExportParticipantsCSVView.as_view(), name="export_csv"),
    path("gerador-link/", LinkGeneratorView.as_view(), name="link_generator"),
    path("emissao-massa/", BulkSendCertificatesView.as_view(), name="bulk_issue"),
    path("resetar/<uuid:registration_id>/", ResetCertificateStatusView.as_view(), name="reset_status"),
    path("excluir/<uuid:registration_id>/", DeleteRegistrationView.as_view(), name="delete"),
    path(
        "enviar/<uuid:registration_id>/",
        SendCertificateView.as_view(),
        name="send"
    ),
    # Verificação pública — URL direta via QR Code
    path(
        "verificar/<str:numeric_code>/",
        VerifyCertificateView.as_view(),
        name="verify_direct"
    ),
    # Verificação por formulário
    path("verificar/", VerifyCertificateView.as_view(), name="verify"),
]
