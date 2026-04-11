"""
apps/registrations/views.py
"""
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.utils import timezone
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from apps.core.models import Course
from .models import Registration
from .forms import RegistrationForm


class RegistrationCreateView(CreateView):
    """Exibe e processa o formulário de solicitação de certificado do participante."""
    model = Registration
    form_class = RegistrationForm
    template_name = "registrations/form.html"
    success_url = reverse_lazy("registrations:registration_success")
    is_pre_event = False  # Define se a view é de pré-evento

    def dispatch(self, request, *args, **kwargs):
        """
        Blindagem: Verifica se a solicitação de certificado está dentro do período permitido.
        """
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        now = timezone.now()
        
        # Trava: Início da Solicitação (se definido)
        if course.certificate_start and now < course.certificate_start:
            return render(request, "registrations/time_locked.html", {
                "course": course, 
                "action_type": "solicitação de certificado", 
                "lock_state": "early", 
                "target_date": course.certificate_start
            }, status=403)
            
        # Trava: Término da Solicitação (se definido)
        if course.certificate_end and now > course.certificate_end:
            return render(request, "registrations/time_locked.html", {
                "course": course, 
                "action_type": "solicitação de certificado", 
                "lock_state": "late", 
                "target_date": course.certificate_end
            }, status=403)
            
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
        Lógica Sênior: Match de CPF para atualização de dados ou criação, 
        seguido de disparo automático de certificado via Celery se houver presença confirmada.
        Inclui trava de segurança para impedir re-emissão de certificados já enviados e
        lógica para permitir automação em inscrições pendentes com check-in realizado.
        """
        # a) Recuperação de dados base
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        cpf = form.cleaned_data.get('cpf')
        
        # b) Busca por inscrição existente (Match de CPF e Curso)
        inscricao = Registration.objects.filter(cpf=cpf, course=course).first()
        
        if inscricao:
            # Caso 1: Certificado já foi enviado (SENT)
            if inscricao.status == Registration.Status.SENT:
                self.request.session['already_requested'] = True
                self.request.session['course_name'] = course.name
                self.request.session['course_date'] = course.start_date.strftime('%d/%m/%Y')
                
                # OBRIGATÓRIO: Injeta o objeto na view para que self.get_success_url() não falhe
                self.object = inscricao
                return HttpResponseRedirect(self.get_success_url())
            
            # Caso 2: Inscrição PENDENTE - Permite atualização e tentativa de automação
            # Atualiza: Absorve correções feitas pelo aluno no formulário
            for field, value in form.cleaned_data.items():
                setattr(inscricao, field, value)
            inscricao.save()

            self.object = inscricao
            auto_emitted = False

            # Condição de Automação: Se não for pré-evento E tiver presença confirmada agora
            if not self.is_pre_event and inscricao.attended:
                from apps.certificates.tasks import issue_certificate_task
                issue_certificate_task.delay(str(inscricao.pk))
                auto_emitted = True
                self.request.session['auto_emitted'] = True
            else:
                # Se ainda não tem check-in, marca como duplicidade pendente visual
                self.request.session['already_pending'] = True

            # Injeção de dados do evento para feedback na tela de sucesso
            self.request.session['course_name'] = course.name
            self.request.session['course_date'] = course.start_date.strftime('%d/%m/%Y')
            
            return HttpResponseRedirect(self.get_success_url())

        # d) Nova Inscrição: Caso não exista match prévio
        inscricao = form.save(commit=False)
        inscricao.course = course
        # Sincroniza dados históricos para o modelo de inscrição
        inscricao.course_name = course.name
        inscricao.course_date = course.start_date
        inscricao.course_workload = course.hours
        inscricao.save()

        self.object = inscricao
        auto_emitted = False

        # e) Condição de Automação para novas inscrições
        if not self.is_pre_event and inscricao.attended:
            from apps.certificates.tasks import issue_certificate_task
            issue_certificate_task.delay(str(inscricao.pk))
            auto_emitted = True

        # f) Persistência de estado na sessão para a view de sucesso
        self.request.session['auto_emitted'] = auto_emitted
        self.request.session['registered_first_name'] = self.object.full_name.split()[0] if self.object.full_name else ""
        
        # Injeção de dados do evento na sessão para feedback na tela de sucesso
        self.request.session['course_name'] = course.name
        self.request.session['course_date'] = course.start_date.strftime('%d/%m/%Y')
        
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
    is_pre_event = True  # Marca como pré-evento para evitar automação de certificado

    def dispatch(self, request, *args, **kwargs):
        """
        Blindagem: Verifica se o período de inscrição pré-evento é válido.
        """
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        now = timezone.now()

        # Trava: Início das Inscrições (se definido)
        if course.registration_start and now < course.registration_start:
            return render(request, "registrations/time_locked.html", {
                "course": course, 
                "action_type": "inscrição", 
                "lock_state": "early", 
                "target_date": course.registration_start
            }, status=403)

        # Trava: Término das Inscrições (se definido)
        if course.registration_end and now > course.registration_end:
            return render(request, "registrations/time_locked.html", {
                "course": course, 
                "action_type": "inscrição", 
                "lock_state": "late", 
                "target_date": course.registration_end
            }, status=403)

        # Pula o dispatch da RegistrationCreateView (que checa certificate_start/end)
        return super(RegistrationCreateView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Proteção contra duplicidade no pré-evento e injeção de dados na sessão.
        """
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        cpf = form.cleaned_data.get('cpf')
        
        # Bloqueio de duplicidade: Garante que o CPF não se inscreva duas vezes no mesmo curso
        if Registration.objects.filter(cpf=cpf, course=course).exists():
            form.add_error('cpf', 'Você já está inscrito neste evento.')
            return self.form_invalid(form)
            
        # Prossegue com o salvamento base e injeção de flags de sessão
        response = super().form_valid(form)
        
        self.request.session['is_event'] = True
        self.request.session['course_name'] = self.object.course.name
        self.request.session['course_date'] = self.object.course.start_date.strftime('%d/%m/%Y')
        
        return response


class RegistrationSuccessView(TemplateView):
    """Tela de agradecimento após envio do formulário."""
    template_name = "registrations/registration_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Recupera e remove os dados da sessão para exibição única e limpa
        context["first_name"] = self.request.session.pop("registered_first_name", "")
        context["is_event"] = self.request.session.pop("is_event", False)
        context["course_name"] = self.request.session.pop("course_name", "")
        context["course_date"] = self.request.session.pop("course_date", "")
        context["auto_emitted"] = self.request.session.pop("auto_emitted", False)
        context["already_requested"] = self.request.session.pop("already_requested", False)
        context["already_pending"] = self.request.session.pop("already_pending", False)
        
        return context
