"""
apps/registrations/urls.py
"""
from django.urls import path
from .views import (
    RegistrationCreateView, RegistrationSuccessView, EventRegistrationCreateView,
    RecurringEventRegistrationView, RecurringEventCertificateView
)
from apps.core.views import (
    PublicCheckinView, ToggleMassPresenceView, 
    PublicTogglePresenceView, PublicSendLinkEmailView,
    PublicSessionCheckinView, ToggleMassSessionPresenceView, PublicToggleSessionPresenceView
)

app_name = "registrations"

urlpatterns = [
    path("solic-cert-<slug:slug>/", RegistrationCreateView.as_view(), name="form"),
    path("inscricao/<slug:slug>/", EventRegistrationCreateView.as_view(), name="event_form"),
    
    # Eventos Recorrentes
    path("recorrente/inscricao/<slug:slug>/", RecurringEventRegistrationView.as_view(), name="recurring_event_form"),
    path("recorrente/solic-cert/<slug:slug>/", RecurringEventCertificateView.as_view(), name="recurring_cert_form"),
    
    path("obrigado/", RegistrationSuccessView.as_view(), name="registration_success"),
    
    # Credenciamento Público (Magic Link)
    path("credenciamento/<uuid:checkin_hash>/", PublicCheckinView.as_view(), name="public_checkin"),
    path("credenciamento/<uuid:checkin_hash>/massa/", ToggleMassPresenceView.as_view(), name="toggle_mass_presence"),
    path("credenciamento/toggle/<uuid:reg_id>/", PublicTogglePresenceView.as_view(), name="public_toggle_presence"),
    path("credenciamento/<uuid:checkin_hash>/enviar-email/", PublicSendLinkEmailView.as_view(), name="public_send_link_email"),

    # Credenciamento de Sessão (Recorrentes)
    path("credenciamento/sessao/<uuid:checkin_hash>/", PublicSessionCheckinView.as_view(), name="public_session_checkin"),
    path("credenciamento/sessao/<uuid:checkin_hash>/massa/", ToggleMassSessionPresenceView.as_view(), name="toggle_mass_session_presence"),
    path("credenciamento/sessao/toggle/<int:session_id>/<uuid:reg_id>/", PublicToggleSessionPresenceView.as_view(), name="public_toggle_session_presence"),
]
