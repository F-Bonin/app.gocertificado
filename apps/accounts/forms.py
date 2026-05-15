from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import UserProfile

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")

class FirstAccessPasswordForm(forms.Form):
    new_password = forms.CharField(label="Nova Senha", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite a nova senha'}))
    confirm_password = forms.CharField(label="Confirme a Nova Senha", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repita a nova senha'}))

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('new_password') != cleaned_data.get('confirm_password'):
            raise ValidationError("As senhas não conferem.")
        return cleaned_data

class TeamMemberForm(forms.ModelForm):
    first_name = forms.CharField(label="Nome do Membro", max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="E-mail de Acesso", widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = [
            'perm_dashboard', 'perm_company', 'perm_cert_design',
            'perm_instructors', 'perm_nps', 'perm_custom_forms',
            'perm_standard_events', 'perm_recurring_events',
            'perm_my_events', 'perm_participants', 'perm_certificates_panel'
        ]
        widgets = {field: forms.CheckboxInput(attrs={'class': 'form-check-input form-switch'}) for field in fields}

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user_id:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['email'].initial = self.instance.user.email

    def clean_email(self):
        email = self.cleaned_data['email']
        qs = User.objects.filter(email=email)
        if self.instance and self.instance.user_id:
            qs = qs.exclude(id=self.instance.user.id)
        if qs.exists():
            raise ValidationError("Este e-mail já está cadastrado em outra conta.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.pk:
            if self.company and self.company.users.count() >= 3:
                raise ValidationError("Sua organização atingiu o limite máximo de 3 usuários (1 Admin + 2 Membros).")
        return cleaned_data
