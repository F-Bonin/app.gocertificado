from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from apps.core.models import Company
from .models import UserProfile
from .forms import UserRegistrationForm


class UserRegistrationView(CreateView):
    template_name = "accounts/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("certificates:dashboard")

    def form_valid(self, form):
        # 1. Salva o usuário
        user = form.save()
        
        # 2. Cria uma empresa padrão para este usuário (Multitenancy)
        company = Company.objects.create(name=f"Empresa de {user.username}")
        
        # 3. Cria o perfil vinculando usuário e empresa
        UserProfile.objects.create(user=user, company=company)
        
        # 4. Login automático após o cadastro
        login(self.request, user)
        
        return redirect(self.success_url)


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")
