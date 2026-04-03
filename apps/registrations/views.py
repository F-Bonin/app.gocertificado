"""
apps/registrations/views.py
"""
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from .models import Registration
from .forms import RegistrationForm


class RegistrationCreateView(CreateView):
    """Exibe e processa o formulário de inscrição do participante."""
    model = Registration
    form_class = RegistrationForm
    template_name = "registrations/form.html"
    success_url = reverse_lazy("registrations:registration_success")

    def get_initial(self):
        initial = super().get_initial()
        from apps.core.models import Course
        from django.shortcuts import get_object_or_404
        course = get_object_or_404(Course, link_hash=self.kwargs.get('link_hash'))
        
        initial.update({
            "course_name": course.name,
            "course_date": course.start_date,
            "city": course.city,
            "state": course.state,
            "course_workload": course.hours,
            "institution_name": course.institution_name,
            "institution_street": course.institution_street,
            "institution_number": course.institution_number,
            "institution_neighborhood": course.institution_neighborhood,
            "institution_complement": course.institution_complement,
        })
        return initial

    def form_valid(self, form):
        from django.shortcuts import get_object_or_404
        from django.http import HttpResponseRedirect
        from apps.core.models import Course
        from apps.registrations.models import Registration
        
        # 1. Busca o curso real pelo hash da URL
        course = get_object_or_404(Course, link_hash=self.kwargs.get('link_hash'))
        
        # Trava: Impede o mesmo CPF no MESMO treinamento/data (mesmo objeto Course)
        if Registration.objects.filter(cpf=form.instance.cpf, course=course).exists():
            form.add_error('cpf', 'Este CPF já está inscrito nesta turma/data deste treinamento.')
            return self.form_invalid(form)
            
        # 2. Salva a inscrição no banco com commit=False para injetar a FK
        inscricao = form.save(commit=False)
        inscricao.course = course
        inscricao.save()
        
        self.object = inscricao
        
        # 3. Configura a sessão para a tela de obrigado
        first_name = self.object.full_name.split()[0] if self.object.full_name else ""
        self.request.session['registered_first_name'] = first_name
        
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.core.models import Course
        from django.shortcuts import get_object_or_404
        context['course'] = get_object_or_404(Course, link_hash=self.kwargs.get('link_hash'))
        return context


class RegistrationSuccessView(TemplateView):
    """Tela de agradecimento após envio do formulário."""
    template_name = "registrations/registration_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Recupera e remove o nome da sessão simultaneamente
        context["first_name"] = self.request.session.pop("registered_first_name", "")
        return context
