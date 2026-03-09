"""
apps/registrations/urls.py
"""
from django.urls import path
from .views import RegistrationCreateView, RegistrationSuccessView

app_name = "registrations"

urlpatterns = [
    path("inscricao/<uuid:link_hash>/", RegistrationCreateView.as_view(), name="form"),
    path("obrigado/", RegistrationSuccessView.as_view(), name="registration_success"),
]
