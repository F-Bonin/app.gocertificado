from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, View
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
import uuid

from apps.core.models import Company
from .models import UserProfile
from .forms import UserRegistrationForm, TeamMemberForm, FirstAccessPasswordForm

class UserRegistrationView(CreateView):
    template_name = "accounts/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("certificates:dashboard")

    def form_valid(self, form):
        user = form.save()
        company = Company.objects.create(name=f"Empresa de {user.username}")
        UserProfile.objects.create(user=user, company=company, is_company_admin=True)
        login(self.request, user)
        return redirect(self.success_url)

class CustomLoginView(LoginView):
    template_name = "accounts/login.html"

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")

class ChangeFirstPasswordView(LoginRequiredMixin, View):
    template_name = "accounts/change_password.html"

    def get(self, request):
        return render(request, self.template_name, {'form': FirstAccessPasswordForm()})

    def post(self, request):
        form = FirstAccessPasswordForm(request.POST)
        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            profile = user.profile
            profile.must_change_password = False
            profile.save(update_fields=['must_change_password'])
            update_session_auth_hash(request, user)
            messages.success(request, "Senha alterada com sucesso!")
            return redirect('certificates:dashboard')
        return render(request, self.template_name, {'form': form})

class TeamListView(LoginRequiredMixin, ListView):
    model = UserProfile
    template_name = "accounts/team_list.html"
    context_object_name = "team"

    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, 'profile') and not request.user.profile.is_company_admin:
            messages.error(request, "Acesso Restrito: Apenas o gestor da conta pode gerenciar a equipe.")
            return redirect('certificates:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return UserProfile.objects.filter(company=self.request.user.profile.company).order_by('-is_company_admin', 'user__first_name')

class TeamCreateView(LoginRequiredMixin, CreateView):
    model = UserProfile
    form_class = TeamMemberForm
    template_name = "accounts/team_form.html"
    success_url = reverse_lazy("accounts:team_list")

    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, 'profile') and not request.user.profile.is_company_admin:
            return redirect('certificates:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.user.profile.company
        return kwargs

    def form_valid(self, form):
        company = self.request.user.profile.company
        email = form.cleaned_data['email']
        first_name = form.cleaned_data['first_name']

        username = f"{email.split('@')[0]}_{str(uuid.uuid4())[:4]}"
        user = User.objects.create_user(username=username, email=email, password="Go123456%", first_name=first_name)
        
        profile = form.save(commit=False)
        profile.user = user
        profile.company = company
        profile.is_company_admin = False
        profile.must_change_password = True
        profile.save()

        messages.success(self.request, f"Membro {first_name} adicionado! O acesso inicial é com a senha 'Go123456%'.")
        return super().form_valid(form)

class TeamUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = TeamMemberForm
    template_name = "accounts/team_form.html"
    success_url = reverse_lazy("accounts:team_list")

    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, 'profile') and not request.user.profile.is_company_admin:
            return redirect('certificates:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return UserProfile.objects.filter(company=self.request.user.profile.company, is_company_admin=False)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.user.profile.company
        return kwargs

    def form_valid(self, form):
        profile = form.save()
        user = profile.user
        user.first_name = form.cleaned_data['first_name']
        user.email = form.cleaned_data['email']
        user.save(update_fields=['first_name', 'email'])
        messages.success(self.request, "Permissões atualizadas com sucesso!")
        return super().form_valid(form)

class TeamDeleteView(LoginRequiredMixin, DeleteView):
    model = UserProfile
    template_name = "accounts/team_confirm_delete.html"
    success_url = reverse_lazy("accounts:team_list")

    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, 'profile') and not request.user.profile.is_company_admin:
            return redirect('certificates:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return UserProfile.objects.filter(company=self.request.user.profile.company, is_company_admin=False)

    def form_valid(self, form):
        user = self.get_object().user
        response = super().form_valid(form)
        user.delete() 
        messages.success(self.request, "Membro removido da equipe com sucesso.")
        return response

class TeamSendInviteEmailView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not request.user.profile.is_company_admin:
            return JsonResponse({"ok": False, "error": "Acesso Negado"})
            
        profile = get_object_or_404(UserProfile, pk=pk, company=request.user.profile.company)
        try:
            subject = f"Acesso à Plataforma GoCertificado"
            message = (
                f"Olá, {profile.user.first_name}!\n\n"
                f"Você foi convidado(a) para administrar os eventos na plataforma GoCertificado pela empresa {profile.company.name}.\n\n"
                f"Para acessar, utilize os dados provisórios abaixo:\n\n"
                f"URL de Acesso: {request.scheme}://{request.get_host()}/accounts/login/\n"
                f"Seu E-mail: {profile.user.email}\n"
                f"Senha Inicial: Go123456%\n\n"
                f"Aviso de Segurança: Ao fazer o login, o sistema exigirá que você redefina esta senha por uma de sua preferência.\n\n"
                f"Bem-vindo(a)!"
            )
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [profile.user.email], fail_silently=False)
            return JsonResponse({"ok": True, "msg": "E-mail de acesso enviado com sucesso!"})
        except Exception as e:
            return JsonResponse({"ok": False, "error": str(e)})
