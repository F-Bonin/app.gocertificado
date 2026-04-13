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
    """Exibe e processa o formulário de solicitação de certificado (PÓS-EVENTO)."""
    model = Registration
    form_class = RegistrationForm
    template_name = "registrations/form.html"
    success_url = reverse_lazy("registrations:registration_success")

    def dispatch(self, request, *args, **kwargs):
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        # Ajuste Sênior: certificate_end substituiu expires_at conforme CURRENT_STATE.md
        if course.certificate_end and timezone.now() > course.certificate_end:
            return HttpResponseForbidden(
                "<div style='text-align:center; margin-top:50px; font-family:sans-serif;'>"
                "<h2>A solicitação de certificado para este treinamento foi encerrada.</h2>"
                "<p>O prazo limite para preenchimento deste formulário expirou.</p>"
                "</div>"
            )
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        initial.update({
            "institution_name": course.institution_name,
            "institution_street": course.institution_street,
            "institution_number": course.institution_number,
            "institution_neighborhood": course.institution_neighborhood,
            "institution_complement": course.institution_complement,
        })
        return initial

    def form_valid(self, form):
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        cpf = form.cleaned_data.get('cpf')
        full_name = form.cleaned_data.get('full_name', '')
        # Ajuste Sênior: Extração segura do primeiro nome para evitar exibição de lista
        first_name = full_name.split()[0] if full_name else ""
        course_date_str = course.start_date.strftime('%d/%m/%Y') if course.start_date else ""

        from apps.registrations.models import Registration
        reg = Registration.objects.filter(cpf=cpf, course=course).first()

        if not reg:
            # REGRA 5: CPF não encontrado
            msg = (f"{first_name}, seu número de CPF não consta em nossa base de dados para o evento "
                   f"{course.name} realizado no dia {course_date_str}. Pode ser que você tenha digitado "
                   f"seu CPF errado, ou você não tenha feito inscrição para esse evento. Caso não tenha "
                   f"feito a inscrição, entre em contato com o responsável pelo evento. Após realizar sua "
                   f"inscrição, faça a solicitação do seu certificado preenchendo este formulário. Obrigado!")
            form.add_error('cpf', msg)
            return self.form_invalid(form)

        # Atualiza os dados da inscrição existente em vez de duplicar
        for field, value in form.cleaned_data.items():
            setattr(reg, field, value)

        # MOTOR DE REGRAS PÓS-EVENTO
        from apps.certificates.tasks import issue_certificate_task

        if reg.attended:
            if reg.status == Registration.Status.PENDING:
                # REGRA 1
                msg = (f"{first_name}, obrigado! Seus dados foram enviados. Seu Certificado do evento "
                       f"{course.name}, realizado em {course_date_str}, está sendo gerado. Você o receberá no e-mail "
                       f"que informou ao preencher o formulário. Se o e-mail não chegar em sua caixa de entrada, "
                       f"verificar no SPAM ou no lixo eletrônico. Se não o receber, por favor entre em contato "
                       f"com o responsável pelo evento.")
                reg.is_requested = True
                reg.save()
                issue_certificate_task.delay(str(reg.id))
            else:
                # REGRA 2
                msg = (f"{first_name}, Você já solicitou seu certificado do evento {course.name}, "
                       f"realizado em {course_date_str}. Caso não tenha recebido em sua caixa de entrada, "
                       f"verifique o SPAM e Lixo eletrônico. Se já verificou ou teve algum problema com as "
                       f"informações do seu certificado, entre em contato com o responsável pelo evento.")
                reg.is_requested = True
                reg.save()
        else:
            if not reg.is_requested:
                # REGRA 3
                msg = (f"{first_name}, obrigado! Seus dados foram enviados. Seu Certificado do evento "
                       f"{course.name}, realizado em {course_date_str}, está sendo gerado. Assim que sua "
                       f"presença for confirmada você receberá seu certificado no e-mail que informou ao "
                       f"preencher o formulário. Se o e-mail não chegar em sua caixa de entrada, verificar "
                       f"no SPAM ou no lixo eletrônico. Se não o receber, por favor entre em contato com o "
                       f"responsável pelo evento.")
                reg.is_requested = True
                reg.save()
            else:
                # REGRA 4
                msg = (f"{first_name}, Você já solicitou seu certificado do evento {course.name}, "
                       f"realizado em {course_date_str}. Assim que sua presença for confirmada você receberá "
                       f"seu certificado no e-mail que informou ao preencher o formulário. Se o e-mail não "
                       f"chegar em sua caixa de entrada, verificar no SPAM ou no lixo eletrônico. Se não o "
                       f"receber, por favor entre em contato com o responsável pelo evento.")
                reg.save()

        self.request.session['success_message'] = msg
        # Sênior Fix: Preenche o objeto obrigatório do CreateView para não quebrar o redirecionamento
        self.object = reg 
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        """
        Sênior Fix: Recupera o Treinamento no banco de dados via slug da URL
        e injeta no contexto do template para popular os dados visuais do evento
        (Nome, Data, Carga Horária, Local).
        """
        context = super().get_context_data(**kwargs)
        from django.shortcuts import get_object_or_404
        from apps.core.models import Course
        
        # Busca o curso real pelo Slug da URL para garantir segurança
        context['course'] = get_object_or_404(Course, slug=self.kwargs['slug'])
        return context

class EventRegistrationCreateView(RegistrationCreateView):
    """Exibe e processa o formulário de Inscrição (PRÉ-EVENTO)."""
    template_name = "registrations/event_form.html"

    def dispatch(self, request, *args, **kwargs):
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        now = timezone.now()
        
        if course.registration_start and now < course.registration_start:
            return HttpResponseForbidden(
                "<div style='text-align:center; margin-top:50px; font-family:sans-serif;'>"
                "<h2>As inscrições para este evento ainda não começaram.</h2>"
                "</div>"
            )
        if course.registration_end and now > course.registration_end:
            return HttpResponseForbidden(
                "<div style='text-align:center; margin-top:50px; font-family:sans-serif;'>"
                "<h2>As inscrições para este evento foram encerradas.</h2>"
                "</div>"
            )
        return super(RegistrationCreateView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        
        if Registration.objects.filter(cpf=form.instance.cpf, course=course).exists():
            form.add_error('cpf', 'Este CPF já está inscrito nesta turma/data deste evento.')
            return self.form_invalid(form)

        inscricao = form.save(commit=False)
        inscricao.course = course
        inscricao.course_name = course.name
        inscricao.course_date = course.start_date
        inscricao.course_workload = course.hours
        inscricao.is_requested = False
        inscricao.save()

        # Ajuste Sênior: Extração segura do primeiro nome
        first_name = inscricao.full_name.split()[0] if inscricao.full_name else ""
        course_date_str = course.start_date.strftime('%d/%m/%Y') if course.start_date else ""

        # REGRA 0
        self.request.session['success_message'] = (
            f"{first_name}, obrigado! Seus dados foram registrados e enviados ao responsável "
            f"pelo evento {course.name} a ser realizado em {course_date_str}. Bom evento para você! Até breve!"
        )
        # Sênior Fix: Preenche o objeto obrigatório do CreateView para não quebrar o redirecionamento
        self.object = inscricao 
        return HttpResponseRedirect(self.get_success_url())

class RegistrationSuccessView(TemplateView):
    template_name = "registrations/registration_success.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["success_message"] = self.request.session.pop("success_message", "Ação processada com sucesso.")
        return context
