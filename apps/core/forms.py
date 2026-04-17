from django import forms
from .models import Company, Instructor, Course, NPSForm, NPSQuestion
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
            "expires_at", "no_certificate",
            "cep", "institution_name", "institution_street", "institution_number",
            "institution_neighborhood", "institution_complement",
            "city", "state",
            "signature_1", "signature_2", "signature_3",
            "certificate_template",
            "nps_form"
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "start_date": forms.DateInput(format='%Y-%m-%d', attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(format='%Y-%m-%d', attrs={"class": "form-control", "type": "date"}),
            "registration_start": forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local', 'class': 'form-control'}),
            "registration_end": forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local', 'class': 'form-control'}),
            "expires_at": forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local', 'class': 'form-control'}),
            "no_certificate": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "check_no_certificate"}),
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
        }
    def __init__(self, *args, **kwargs):
        company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)
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