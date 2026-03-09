from django import forms
from .models import Company, Instructor, Course


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name", "cnpj", "website", "logo"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "cnpj": forms.TextInput(attrs={"class": "form-control", "placeholder": "00.000.000/0000-00"}),
            "website": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://..."}),
            "logo": forms.FileInput(attrs={"class": "form-control"}),
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
            "institution_name", "institution_street", "institution_number",
            "institution_neighborhood", "institution_complement",
            "city", "state",
            "signature_1", "signature_2", "signature_3"
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "state": forms.TextInput(attrs={"class": "form-control", "maxlength": "2", "placeholder": "UF"}),
            "hours": forms.NumberInput(attrs={"class": "form-control"}),
            "institution_name": forms.TextInput(attrs={"class": "form-control"}),
            "institution_street": forms.TextInput(attrs={"class": "form-control"}),
            "institution_number": forms.TextInput(attrs={"class": "form-control"}),
            "institution_neighborhood": forms.TextInput(attrs={"class": "form-control"}),
            "institution_complement": forms.TextInput(attrs={"class": "form-control"}),
            "signature_1": forms.Select(attrs={"class": "form-select"}),
            "signature_2": forms.Select(attrs={"class": "form-select"}),
            "signature_3": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)
        
        # Define initial num_signatures if editing
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

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if end_date < start_date:
                self.add_error("end_date", "A data de término não pode ser anterior à data de início.")

        return cleaned_data
