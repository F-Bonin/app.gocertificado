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
        """
        Preenche os dados iniciais do formulário baseando-se no curso encontrado via Slug.
        Removido o uso de self.request.GET para evitar manipulação via Query String.
        """
        initial = super().get_initial()
        from apps.core.models import Course
        from django.shortcuts import get_object_or_404
        
        # Busca direta no banco de dados utilizando o Slug amigável da URL
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        
        # Preenche os campos de endereço da instituição baseados no curso
        initial.update({
            "institution_name": course.institution_name,
            "institution_street": course.institution_street,
            "institution_number": course.institution_number,
            "institution_neighborhood": course.institution_neighborhood,
            "institution_complement": course.institution_complement,
        })
        return initial

    def form_valid(self, form):
        """
        Processa o salvamento da inscrição associando o curso via busca direta pelo Slug.
        """
        from django.shortcuts import get_object_or_404
        from django.http import HttpResponseRedirect
        from apps.core.models import Course
        from apps.registrations.models import Registration
        
        # 1. Busca o curso real pelo Slug da URL para garantir segurança e integridade
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        
        # Trava: Impede o mesmo CPF no MESMO treinamento/data (mesmo objeto Course)
        if Registration.objects.filter(cpf=form.instance.cpf, course=course).exists():
            form.add_error('cpf', 'Este CPF já está inscrito nesta turma/data deste treinamento.')
            return self.form_invalid(form)
            
        # 2. Salva a inscrição no banco com commit=False para injetar a FK do curso
        inscricao = form.save(commit=False)
        inscricao.course = course
        
        # Sincroniza dados legados para garantir persistência histórica
        inscricao.course_name = course.name
        inscricao.course_date = course.start_date
        inscricao.course_workload = course.hours
        
        inscricao.save()
        
        self.object = inscricao
        
        # 3. Configura a sessão para a tela de obrigado
        first_name = self.object.full_name.split()[0] if self.object.full_name else ""
        self.request.session['registered_first_name'] = first_name
        
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        """
        Repassa os dados do objeto course para o contexto da página de inscrição de forma segura.
        """
        context = super().get_context_data(**kwargs)
        from apps.core.models import Course
        from django.shortcuts import get_object_or_404
        
        # Busca o curso novamente via slug para garantir que os dados exibidos no template venham do banco
        context['course'] = get_object_or_404(Course, slug=self.kwargs['slug'])
        return context


class RegistrationSuccessView(TemplateView):
    """Tela de agradecimento após envio do formulário."""
    template_name = "registrations/registration_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Recupera e remove o nome da sessão simultaneamente
        context["first_name"] = self.request.session.pop("registered_first_name", "")
        return context
