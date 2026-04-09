"""
apps/registrations/urls.py
"""
from django.urls import path
from .views import RegistrationCreateView, RegistrationSuccessView, EventRegistrationCreateView

app_name = "registrations"

urlpatterns = [
    path("solic-cert-<slug:slug>/", RegistrationCreateView.as_view(), name="form"),
    path("inscricao/<slug:slug>/", EventRegistrationCreateView.as_view(), name="event_form"),
    path("obrigado/", RegistrationSuccessView.as_view(), name="registration_success"),
]
