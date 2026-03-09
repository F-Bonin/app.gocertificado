"""
apps/registrations/forms.py
Formulário de inscrição do participante.
"""
import re
from django import forms
from apps.core.models import Instructor
from .models import Registration

ESTADOS_BR = [
    ("", "Selecione o estado"),
    ("AC", "Acre"), ("AL", "Alagoas"), ("AP", "Amapá"), ("AM", "Amazonas"),
    ("BA", "Bahia"), ("CE", "Ceará"), ("DF", "Distrito Federal"),
    ("ES", "Espírito Santo"), ("GO", "Goiás"), ("MA", "Maranhão"),
    ("MT", "Mato Grosso"), ("MS", "Mato Grosso do Sul"), ("MG", "Minas Gerais"),
    ("PA", "Pará"), ("PB", "Paraíba"), ("PR", "Paraná"), ("PE", "Pernambuco"),
    ("PI", "Piauí"), ("RJ", "Rio de Janeiro"), ("RN", "Rio Grande do Norte"),
    ("RS", "Rio Grande do Sul"), ("RO", "Rondônia"), ("RR", "Roraima"),
    ("SC", "Santa Catarina"), ("SP", "São Paulo"), ("SE", "Sergipe"),
    ("TO", "Tocantins"),
]


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = [
            "full_name", "gender", "custom_gender", "profession",
            "birth_date", "email", "whatsapp",
            "rg", "cpf", "address",
            "institution_name", "institution_street", "institution_number",
            "institution_neighborhood", "institution_complement",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "form-control", "placeholder": "Nome completo conforme documento"
            }),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "custom_gender": forms.TextInput(attrs={
                "class": "form-control", "placeholder": "Informe seu gênero"
            }),
            "profession": forms.TextInput(attrs={
                "class": "form-control", "placeholder": "Sua profissão"
            }),
            "birth_date": forms.DateInput(attrs={
                "class": "form-control", "type": "date"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control", "placeholder": "seu@email.com"
            }),
            "whatsapp": forms.TextInput(attrs={
                "class": "form-control", "placeholder": "(11) 99999-9999"
            }),
            "rg": forms.TextInput(attrs={"class": "form-control"}),
            "cpf": forms.TextInput(attrs={
                "class": "form-control", "placeholder": "000.000.000-00"
            }),
            "address": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Rua, número, bairro, cidade — CEP"
            }),
            "institution_name": forms.TextInput(attrs={"class": "form-control"}),
            "institution_street": forms.TextInput(attrs={"class": "form-control"}),
            "institution_number": forms.TextInput(attrs={"class": "form-control"}),
            "institution_neighborhood": forms.TextInput(attrs={"class": "form-control"}),
            "institution_complement": forms.TextInput(attrs={"class": "form-control"}),
        }
        labels = {
            "full_name": "Nome completo",
            "birth_date": "Data de nascimento",
            "email": "E-mail",
            "whatsapp": "WhatsApp (com DDD)",
            "rg": "RG",
            "cpf": "CPF",
            "address": "Endereço completo",
            "institution_name": "Nome da Instituição",
            "institution_street": "Rua/Avenida",
            "institution_number": "Número",
            "institution_neighborhood": "Bairro",
            "institution_complement": "Complemento",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_cpf(self):
        cpf = self.cleaned_data.get("cpf", "")
        digits = re.sub(r"\D", "", cpf)
        if len(digits) != 11:
            raise forms.ValidationError("CPF inválido. Informe os 11 dígitos.")
        # Validação de dígitos verificadores
        if digits == digits[0] * 11:
            raise forms.ValidationError("CPF inválido.")
        for i in range(9, 11):
            s = sum(int(digits[j]) * (i + 1 - j) for j in range(i))
            expected = (s * 10 % 11) % 10
            if expected != int(digits[i]):
                raise forms.ValidationError("CPF inválido.")
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"

    def clean_whatsapp(self):
        wpp = re.sub(r"\D", "", self.cleaned_data.get("whatsapp", ""))
        if len(wpp) < 10 or len(wpp) > 11:
            raise forms.ValidationError(
                "WhatsApp inválido. Informe DDD + número (10 ou 11 dígitos)."
            )
        return wpp
