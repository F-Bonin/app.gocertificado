"""
apps/registrations/forms.py
Formulário de solicitação de certificado do participante.
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
            "rg", "cpf", 
            "cep", "street", "number", "complement", "neighborhood", "city", "state",
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
            "birth_date": forms.DateInput(format='%Y-%m-%d', attrs={
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
            "cep": forms.TextInput(attrs={
                "class": "form-control", "placeholder": "00000-000", "id": "id_cep"
            }),
            "street": forms.TextInput(attrs={
                "class": "form-control", "id": "id_street", "readonly": True
            }),
            "number": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "complement": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "neighborhood": forms.TextInput(attrs={
                "class": "form-control", "id": "id_neighborhood", "readonly": True
            }),
            "city": forms.TextInput(attrs={
                "class": "form-control", "id": "id_city", "readonly": True
            }),
            "state": forms.TextInput(attrs={
                "class": "form-control", "id": "id_state", "readonly": True
            }),
            "institution_name": forms.TextInput(attrs={"class": "form-control"}),
            "institution_street": forms.TextInput(attrs={"class": "form-control"}),
            "institution_number": forms.TextInput(attrs={"class": "form-control"}),
            "institution_neighborhood": forms.TextInput(attrs={"class": "form-control"}),
            "institution_complement": forms.TextInput(attrs={"class": "form-control"}),
        }
        labels = {
            "full_name": "Nome completo",
            "gender": "Gênero",
            "custom_gender": "Gênero Personalizado (Qual?)",
            "birth_date": "Data de nascimento",
            "email": "E-mail",
            "whatsapp": "WhatsApp (com DDD)",
            "rg": "RG",
            "cpf": "CPF",
            "cep": "CEP",
            "street": "Rua",
            "number": "Número",
            "complement": "Complemento",
            "neighborhood": "Bairro",
            "city": "Cidade",
            "state": "Estado",
            "institution_name": "Nome da Instituição",
            "institution_street": "Rua/Avenida",
            "institution_number": "Número",
            "institution_neighborhood": "Bairro",
            "institution_complement": "Complemento",
        }

    def __init__(self, *args, **kwargs):
        # Extração de contexto para controle de obrigatoriedade dinâmica
        self.course = kwargs.pop('course', None)
        self.is_cert_request = kwargs.pop('is_cert_request', False)
        super().__init__(*args, **kwargs)

        if self.course:
            # Identifica se o formulário em uso é customizado baseado no contexto (Inscrição vs Certificado)
            custom_form = self.course.custom_cert_form if self.is_cert_request else self.course.custom_reg_form
            
            if custom_form:
                # Se for CUSTOMIZADO: Afrouxamos todos os campos EXCETO a Identidade Core (Segurança)
                for field_name, field in self.fields.items():
                    if field_name not in ['full_name', 'cpf', 'email', 'birth_date']:
                        field.required = False
            else:
                # Formulário Padrão: Todos os dados pessoais e endereço são estritamente obrigatórios
                mandatory_fields = [
                    'full_name', 'cpf', 'email', 'birth_date', 'gender', 
                    'profession', 'whatsapp', 'rg', 'cep', 'street', 
                    'number', 'complement', 'neighborhood', 'city', 'state'
                ]
                for field in mandatory_fields:
                    if field in self.fields:
                        self.fields[field].required = True

    def clean_cpf(self):
        cpf_val = self.cleaned_data.get("cpf") or ""
        digits = re.sub(r"\D", "", cpf_val)
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
        val = self.cleaned_data.get("whatsapp") or ""
        wpp = re.sub(r"\D", "", val)
        if not wpp:
            return ""
        if len(wpp) < 10 or len(wpp) > 11:
            raise forms.ValidationError("WhatsApp inválido. Informe DDD + número (10 ou 11 dígitos).")
        return wpp
