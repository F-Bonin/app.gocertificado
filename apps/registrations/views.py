"""
apps/registrations/views.py
"""
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.utils import timezone
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from apps.core.models import Course
from .models import Registration
from .forms import RegistrationForm


class RegistrationCreateView(CreateView):
    """Exibe e processa o formulário de solicitação de certificado do participante."""
    model = Registration
    form_class = RegistrationForm
    template_name = "registrations/form.html"
    success_url = reverse_lazy("registrations:registration_success")

    def dispatch(self, request, *args, **kwargs):
        """
        Blindagem: Verifica se o curso já expirou antes de permitir o acesso à View.
        """
        # Busca o curso pelo slug da URL
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        
        # Validação de expiração: Se houver data definida e já tiver passado do prazo
        if course.expires_at and timezone.now() > course.expires_at:
            return HttpResponseForbidden(
                "<div style='text-align:center; margin-top:50px; font-family:sans-serif;'>"
                "<h2>A solicitação de certificado para este treinamento foi encerrada.</h2>"
                "<p>O prazo limite para preenchimento deste formulário expirou.</p>"
                "</div>"
            )
            
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        """
        Preenche os dados iniciais do formulário baseando-se no curso encontrado via Slug.
        Removido o uso de self.request.GET para evitar manipulação via Query String.
        """
        initial = super().get_initial()
        
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
        
        # Busca o curso novamente via slug para garantir que os dados exibidos no template venham do banco
        context['course'] = get_object_or_404(Course, slug=self.kwargs['slug'])
        return context


class EventRegistrationCreateView(RegistrationCreateView):
    """View para inscrição pré-evento (antes do treinamento ocorrer)."""
    template_name = "registrations/event_form.html"

    def dispatch(self, request, *args, **kwargs):
        """
        Blindagem: Verifica se o período de inscrição pré-evento é válido.
        Substitui a lógica de expiração do certificado pela lógica de período de inscrição.
        """
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        now = timezone.now()

        # 1. Validação de Início (Se definido)
        if course.registration_start and now < course.registration_start:
            return HttpResponseForbidden(
                f"<div style='text-align:center; margin-top:50px; font-family:sans-serif;'>"
                f"<h2>As inscrições para este evento ainda não começaram.</h2>"
                f"<p>Início previsto para: {course.registration_start.strftime('%d/%m/%Y às %H:%M')}</p>"
                "</div>"
            )

        # 2. Validação de Término (Se definido)
        if course.registration_end and now > course.registration_end:
            return HttpResponseForbidden(
                "<div style='text-align:center; margin-top:50px; font-family:sans-serif;'>"
                "<h2>As inscrições para este evento foram encerradas.</h2>"
                "<p>O prazo limite para inscrição expirou.</p>"
                "</div>"
            )

        # Pula o dispatch da RegistrationCreateView (que checa expires_at) e vai para a base View
        return super(RegistrationCreateView, self).dispatch(request, *args, **kwargs)


class RegistrationSuccessView(TemplateView):
    """Tela de agradecimento após envio do formulário."""
    template_name = "registrations/registration_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Recupera e remove o nome da sessão simultaneamente
        context["first_name"] = self.request.session.pop("registered_first_name", "")
        return context
