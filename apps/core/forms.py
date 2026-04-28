import datetime
from django import forms
from django.utils import timezone
from django.forms import inlineformset_factory
from .models import Company, Instructor, Course, NPSForm, NPSQuestion, DynamicForm, DynamicField, RecurringEvent, EventSession
from apps.certificates.models import CertificateTemplate

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name", "cnpj", "website", "email"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "cnpj": forms.TextInput(attrs={"class": "form-control", "placeholder": "00.000.000/0000-00"}),
            "website": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://..."}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "contato@empresa.com"}),
        }

class InstructorForm(forms.ModelForm):
    class Meta:
        model = Instructor
        fields = ["full_name", "role", "credentials", "email", "signature_image", "active"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "role": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Diretor, Instrutor"}),
            "credentials": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Eng. de Segurança - CREA 123"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "signature_image": forms.FileInput(attrs={"class": "form-control"}),
            "active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

class CourseForm(forms.ModelForm):
    num_signatures = forms.ChoiceField(
        choices=[('1', '1 Assinatura'), ('2', '2 Assinaturas'), ('3', '3 Assinaturas')],
        label="Quantidade de Assinaturas",
        initial='1',
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = Course
        fields = [
            "name", "start_date", "end_date", "hours",
            "registration_start", "registration_end",
            "certificate_start", "certificate_end", "no_certificate", "global_passkey",
            "cep", "institution_name", "institution_street", "institution_number",
            "institution_neighborhood", "institution_complement",
            "city", "state",
            "signature_1", "signature_2", "signature_3",
            "certificate_template",
            "nps_form",
            "custom_reg_form",
            "custom_cert_form"
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "start_date": forms.DateInput(format='%Y-%m-%d', attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(format='%Y-%m-%d', attrs={"class": "form-control", "type": "date"}),
            "registration_start": forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local', 'class': 'form-control'}),
            "registration_end": forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local', 'class': 'form-control'}),
            "certificate_start": forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local', 'class': 'form-control'}),
            "certificate_end": forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local', 'class': 'form-control'}),
            "no_certificate": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "check_no_certificate"}),
            "global_passkey": forms.TextInput(attrs={"class": "form-control", "placeholder": "Digite a senha do evento..."}),
            "cep": forms.TextInput(attrs={"class": "form-control", "placeholder": "00000-000", "id": "id_course_cep"}),
            "city": forms.TextInput(attrs={"class": "form-control", "id": "id_course_city", "readonly": True}),
            "state": forms.TextInput(attrs={"class": "form-control", "id": "id_course_state", "readonly": True}),
            "hours": forms.NumberInput(attrs={"class": "form-control"}),
            "institution_name": forms.TextInput(attrs={"class": "form-control"}),
            "institution_street": forms.TextInput(attrs={"class": "form-control", "id": "id_course_street", "readonly": True}),
            "institution_number": forms.TextInput(attrs={"class": "form-control"}),
            "institution_neighborhood": forms.TextInput(attrs={"class": "form-control", "id": "id_course_neighborhood", "readonly": True}),
            "institution_complement": forms.TextInput(attrs={"class": "form-control"}),
            "signature_1": forms.Select(attrs={"class": "form-select"}),
            "signature_2": forms.Select(attrs={"class": "form-select"}),
            "signature_3": forms.Select(attrs={"class": "form-select"}),
            "certificate_template": forms.Select(attrs={"class": "form-select"}),
            "nps_form": forms.Select(attrs={"class": "form-select"}),
            "custom_reg_form": forms.Select(attrs={"class": "form-select"}),
            "custom_cert_form": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)
        
        # Autofill inteligente para novos eventos
        if not self.instance.pk:
            now = timezone.now()
            today = now.date()
            tomorrow = today + datetime.timedelta(days=1)
            tomorrow_end = timezone.make_aware(datetime.datetime.combine(tomorrow, datetime.time(23, 59)))
            
            self.initial.setdefault('start_date', today)
            self.initial.setdefault('end_date', today)
            self.initial.setdefault('registration_start', now)
            self.initial.setdefault('registration_end', tomorrow_end)
            self.initial.setdefault('certificate_start', now)
            self.initial.setdefault('certificate_end', tomorrow_end)

        if self.instance.pk:
            if self.instance.signature_3:
                self.initial['num_signatures'] = '3'
            elif self.instance.signature_2:
                self.initial['num_signatures'] = '2'
            else:
                self.initial['num_signatures'] = '1'

        if company:
            instructor_qs = Instructor.objects.filter(company=company, active=True)
            self.fields["signature_1"].queryset = instructor_qs
            self.fields["signature_2"].queryset = instructor_qs
            self.fields["signature_3"].queryset = instructor_qs
            self.fields["certificate_template"].queryset = CertificateTemplate.objects.filter(company=company)
            self.fields["certificate_template"].empty_label = "Modelo Padrão do Sistema"
            self.fields["certificate_template"].help_text = "Se não selecionar nenhum, o sistema usará o Modelo Padrão nativo."
            
            self.fields["nps_form"].queryset = NPSForm.objects.filter(company=company)
            self.fields["nps_form"].empty_label = "Nenhum (Sem feedback)"

            self.fields["custom_reg_form"].queryset = DynamicForm.objects.filter(company=company, form_type='REG')
            self.fields["custom_reg_form"].empty_label = "Modelo Padrão do Sistema"
            
            self.fields["custom_cert_form"].queryset = DynamicForm.objects.filter(company=company, form_type='CERT')
            self.fields["custom_cert_form"].empty_label = "Modelo Padrão do Sistema"

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date:
            if end_date < start_date:
                self.add_error("end_date", "A data de término não pode ser anterior à data de início.")
        return cleaned_data

class NPSFormModelForm(forms.ModelForm):
    class Meta:
        model = NPSForm
        fields = ["name", "is_mandatory"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "is_mandatory": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

class NPSQuestionForm(forms.ModelForm):
    class Meta:
        model = NPSQuestion
        fields = ["text", "question_type", "order"]
        widgets = {
            "text": forms.TextInput(attrs={"class": "form-control"}),
            "question_type": forms.Select(attrs={"class": "form-select"}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
        }

class CertificateDesignForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['logo', 'logo_position', 'custom_template', 'custom_title', 'custom_text_1', 'custom_text_2', 'custom_text_3', 'custom_text_4', 'custom_text_5', 'custom_text_6']
        widgets = {
            'logo_position': forms.Select(attrs={'class': 'form-select'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'custom_title': forms.TextInput(attrs={'class': 'form-control fw-bold text-center'}),
            'custom_text_1': forms.TextInput(attrs={'class': 'form-control'}),
            'custom_text_2': forms.TextInput(attrs={'class': 'form-control'}),
            'custom_text_3': forms.TextInput(attrs={'class': 'form-control'}),
            'custom_text_4': forms.TextInput(attrs={'class': 'form-control'}),
            'custom_text_5': forms.TextInput(attrs={'class': 'form-control'}),
            'custom_text_6': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CertificateTemplateForm(forms.ModelForm):
    class Meta:
        model = CertificateTemplate
        fields = [
            'name', 'background_image', 'title',
            'text_1', 'text_2', 'text_3', 'text_4', 'text_5', 'text_6'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Modelo Padrão, Modelo Imersão'}),
            'background_image': forms.FileInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control fw-bold text-center'}),
            'text_1': forms.TextInput(attrs={'class': 'form-control'}),
            'text_2': forms.TextInput(attrs={'class': 'form-control'}),
            'text_3': forms.TextInput(attrs={'class': 'form-control'}),
            'text_4': forms.TextInput(attrs={'class': 'form-control'}),
            'text_5': forms.TextInput(attrs={'class': 'form-control'}),
            'text_6': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        campos_opcionais = ['title', 'text_1', 'text_2', 'text_3', 'text_4', 'text_5', 'text_6']
        for campo in campos_opcionais:
            if campo in self.fields:
                self.fields[campo].required = False

    def clean(self):
        cleaned_data = super().clean()
        for field in ['title', 'text_1', 'text_2', 'text_3', 'text_4', 'text_5', 'text_6']:
            if not cleaned_data.get(field):
                cleaned_data[field] = " "
        return cleaned_data


class DynamicFormModelForm(forms.ModelForm):
    """Formulário para o modelo DynamicForm (Entidade EAV)."""
    class Meta:
        model = DynamicForm
        fields = ["name", "form_type", "layout_type"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Inscrição Personalizada"}),
            "form_type": forms.RadioSelect(attrs={'class': 'form-check-input'}),
            "layout_type": forms.HiddenInput(),
        }


# Inline Formset para gerenciar campos dinâmicos (Atributos EAV) dentro do formulário de DynamicForm.
DynamicFieldFormSet = inlineformset_factory(
    DynamicForm,
    DynamicField,
    fields=['label', 'field_type', 'is_required', 'options', 'order'],
    extra=0,
    can_delete=True,
    widgets={
        'label': forms.TextInput(attrs={'class': 'form-control'}),
        'field_type': forms.Select(attrs={'class': 'form-select'}),
        'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        'options': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opção 1, Opção 2...'}),
        'order': forms.NumberInput(attrs={'readonly': True, 'class': 'form-control bg-light'}),
    }
)

class RecurringEventForm(forms.ModelForm):
    """Formulário para o modelo RecurringEvent (Eventos Recorrentes)."""
    num_signatures = forms.ChoiceField(
        choices=[('1', '1 Assinatura'), ('2', '2 Assinaturas'), ('3', '3 Assinaturas')],
        label="Quantidade de Assinaturas",
        initial='1',
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = RecurringEvent
        exclude = ['company', 'slug', 'no_certificate', 'created_at']
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "event_type": forms.RadioSelect(attrs={'class': 'form-check-input'}),
            "hours": forms.NumberInput(attrs={"class": "form-control"}),
            "min_frequency": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 100}),
            "global_passkey": forms.TextInput(attrs={"class": "form-control", "placeholder": "Digite a senha do evento..."}),
            "registration_start": forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local', 'class': 'form-control'}),
            "registration_end": forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local', 'class': 'form-control'}),
            "certificate_start": forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local', 'class': 'form-control'}),
            "certificate_end": forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local', 'class': 'form-control'}),
            "signature_1": forms.Select(attrs={"class": "form-select"}),
            "signature_2": forms.Select(attrs={"class": "form-select"}),
            "signature_3": forms.Select(attrs={"class": "form-select"}),
            "certificate_template": forms.Select(attrs={"class": "form-select"}),
            "nps_form": forms.Select(attrs={"class": "form-select"}),
            "custom_reg_form": forms.Select(attrs={"class": "form-select"}),
            "custom_cert_form": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)
        
        # Datas não obrigatórias para suportar links vitalícios via UI
        self.fields['registration_start'].required = False
        self.fields['registration_end'].required = False
        self.fields['certificate_start'].required = False
        self.fields['certificate_end'].required = False

        self.fields['hours'].required = False
        self.fields['hours'].widget.attrs['readonly'] = True
        self.fields['hours'].help_text = "Calculado automaticamente com base na soma dos encontros."

        # Autofill inteligente para novos eventos recorrentes (D+1)
        if not self.instance.pk:
            now = timezone.now()
            today = now.date()
            tomorrow = today + datetime.timedelta(days=1)
            tomorrow_end = timezone.make_aware(datetime.datetime.combine(tomorrow, datetime.time(23, 59)))

            self.initial.setdefault('registration_start', now)
            self.initial.setdefault('registration_end', tomorrow_end)
            self.initial.setdefault('certificate_start', now)
            self.initial.setdefault('certificate_end', tomorrow_end)

        if self.instance.pk:
            if self.instance.signature_3:
                self.initial['num_signatures'] = '3'
            elif self.instance.signature_2:
                self.initial['num_signatures'] = '2'
            else:
                self.initial['num_signatures'] = '1'

        if company:
            instructor_qs = Instructor.objects.filter(company=company, active=True)
            self.fields["signature_1"].queryset = instructor_qs
            self.fields["signature_2"].queryset = instructor_qs
            self.fields["signature_3"].queryset = instructor_qs
            self.fields["certificate_template"].queryset = CertificateTemplate.objects.filter(company=company)
            self.fields["certificate_template"].empty_label = "Modelo Padrão do Sistema"

            self.fields["nps_form"].queryset = NPSForm.objects.filter(company=company)
            self.fields["nps_form"].empty_label = "Nenhum (Sem feedback)"

            self.fields["custom_reg_form"].queryset = DynamicForm.objects.filter(company=company, form_type='REG')
            self.fields["custom_reg_form"].empty_label = "Modelo Padrão do Sistema"

            self.fields["custom_cert_form"].queryset = DynamicForm.objects.filter(company=company, form_type='CERT')
            self.fields["custom_cert_form"].empty_label = "Modelo Padrão do Sistema"

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('hours'):
            cleaned_data['hours'] = 0
        return cleaned_data

class EventSessionForm(forms.ModelForm):
    """Formulário para encontros individuais (EventSession)."""
    class Meta:
        model = EventSession
        fields = [
            'theme', 'content', 'date', 'start_time', 'end_time', 'hours', 
            'location_type', 'condominium_name', 'cep', 
            'institution_name', 'institution_street', 'institution_number', 
            'address_block', 'address_floor', 'address_apt', 'institution_neighborhood', 
            'institution_complement', 'city', 'state', 'country'
        ]
        widgets = {
            'theme': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control'}),
            'hours': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
            'location_type': forms.RadioSelect(attrs={'class': 'form-check-input location-type-radio'}),
            'condominium_name': forms.TextInput(attrs={'class': 'form-control'}),
            'cep': forms.TextInput(attrs={'class': 'form-control'}),
            'institution_name': forms.TextInput(attrs={'class': 'form-control'}),
            'institution_street': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'institution_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address_block': forms.TextInput(attrs={'class': 'form-control'}),
            'address_floor': forms.TextInput(attrs={'class': 'form-control'}),
            'address_apt': forms.TextInput(attrs={'class': 'form-control'}),
            'institution_neighborhood': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'institution_complement': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define os campos estritamente obrigatórios para o Encontro
        mandatory_fields = [
            'theme', 'date', 'start_time', 'end_time', 'cep', 'institution_name', 
            'institution_street', 'institution_number', 'institution_neighborhood', 
            'city', 'state', 'country'
        ]
        for field in mandatory_fields:
            if field in self.fields:
                self.fields[field].required = True
                self.fields[field].label = f"{self.fields[field].label} *"
                
        # Opcionais dependentes da UI, mas que recebem asterisco condicional no label
        self.fields['condominium_name'].label = "Nome do Condomínio *"
        self.fields['address_block'].label = "Bloco *"
        self.fields['address_floor'].label = "Número/Letra do Andar *"
        self.fields['address_apt'].label = "Número do Apartamento/Casa *"

    def clean(self):
        cleaned_data = super().clean()
        
        # Trava de segurança para garantir que hours nunca seja None/vazio
        if not cleaned_data.get('hours'):
            cleaned_data['hours'] = 0
            
        loc_type = cleaned_data.get('location_type')
        
        if loc_type == 'condominio':
            for field in ['condominium_name', 'address_block', 'address_floor', 'address_apt']:
                if not cleaned_data.get(field):
                    self.add_error(field, 'Este campo é obrigatório para endereços em Condomínio.')
        
        return cleaned_data

# Formset para sessões do evento recorrente
EventSessionFormSet = forms.inlineformset_factory(
    RecurringEvent,
    EventSession,
    form=EventSessionForm,
    extra=0,
    can_delete=True
)
