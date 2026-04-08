"""
apps/registrations/urls.py
"""
from django.urls import path
from .views import RegistrationCreateView, RegistrationSuccessView

app_name = "registrations"

urlpatterns = [
    path("solic-cert-<slug:slug>/", RegistrationCreateView.as_view(), name="form"),
    path("obrigado/", RegistrationSuccessView.as_view(), name="registration_success"),
]
