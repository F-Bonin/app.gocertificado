from django import forms
from apps.core.models import Instructor

class LinkGeneratorForm(forms.Form):
    instructor = forms.ModelChoiceField(
        queryset=Instructor.objects.filter(active=True),
        label="Instrutor",
        empty_label="Selecione um instrutor"
    )
    course_name = forms.CharField(label="Nome do Curso", max_length=300)
    city = forms.CharField(label="Cidade", max_length=100)
    state = forms.CharField(label="Estado (UF)", max_length=2)
    course_date = forms.DateField(
        label="Data",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    course_workload = forms.IntegerField(label="Carga Horária (horas)", min_value=1)
