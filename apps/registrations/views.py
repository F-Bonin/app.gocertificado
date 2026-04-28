"""
apps/registrations/views.py
"""
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.utils import timezone
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from apps.core.models import Course, DynamicField
from .models import Registration, DynamicResponse
from .forms import RegistrationForm


class RegistrationCreateView(CreateView):
    """Exibe e processa o formulário de solicitação de certificado (PÓS-EVENTO)."""
    model = Registration
    form_class = RegistrationForm
    template_name = "registrations/form.html"
    success_url = reverse_lazy("registrations:registration_success")

    def dispatch(self, request, *args, **kwargs):
        """
        Blindagem: Verifica se o período de solicitação de certificado é válido.
        Roteamento Temporal Bidirecional (Início e Término).
        """
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        now = timezone.now()

        # 1. Validação de Início (Se definido)
        if course.certificate_start and now < course.certificate_start:
            context = {
                "action_type": "solicitação de certificado",
                "lock_state": "early",
                "target_date": course.certificate_start
            }
            return render(request, "time_locked.html", context, status=403)

        # 2. Validação de Término (Se definido)
        if course.certificate_end and now > course.certificate_end:
            context = {
                "action_type": "solicitação de certificado",
                "lock_state": "late",
                "target_date": course.certificate_end
            }
            return render(request, "time_locked.html", context, status=403)

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

    def get_form_kwargs(self):
        """Injeta o objeto curso e o tipo de solicitação nos argumentos do formulário."""
        kwargs = super().get_form_kwargs()
        kwargs['course'] = get_object_or_404(Course, slug=self.kwargs['slug'])
        kwargs['is_cert_request'] = True
        return kwargs

    def get_template_names(self):
        from django.shortcuts import get_object_or_404
        from apps.core.models import Course
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        if course.custom_cert_form:
            return ["registrations/form_custom.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.shortcuts import get_object_or_404
        from apps.core.models import Course
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        context['course'] = course
        if course.custom_cert_form:
            context['dynamic_fields'] = course.custom_cert_form.fields.all().order_by('order')
        return context

class EventRegistrationCreateView(RegistrationCreateView):
    """Exibe e processa o formulário de Inscrição (PRÉ-EVENTO)."""
    template_name = "registrations/event_form.html"

    def get_template_names(self):
        from django.shortcuts import get_object_or_404
        from apps.core.models import Course
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        if course.custom_reg_form:
            return ["registrations/event_form_custom.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        # Bypass chamando o super da classe avó (CreateView) para não herdar as lógicas do Certificado
        context = super(RegistrationCreateView, self).get_context_data(**kwargs)
        from django.shortcuts import get_object_or_404
        from apps.core.models import Course
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        context['course'] = course
        if course.custom_reg_form:
            context['dynamic_fields'] = course.custom_reg_form.fields.all().order_by('order')
        return context

    def dispatch(self, request, *args, **kwargs):
        """
        Blindagem: Verifica se o período de inscrição pré-evento é válido.
        """
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        now = timezone.now()

        # 1. Validação de Início (Se definido)
        if course.registration_start and now < course.registration_start:
            context = {
                "action_type": "inscrição",
                "lock_state": "early",
                "target_date": course.registration_start
            }
            return render(request, "time_locked.html", context, status=403)

        # 2. Validação de Término (Se definido)
        if course.registration_end and now > course.registration_end:
            context = {
                "action_type": "inscrição",
                "lock_state": "late",
                "target_date": course.registration_end
            }
            return render(request, "time_locked.html", context, status=403)

        return super(RegistrationCreateView, self).dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super(RegistrationCreateView, self).get_form(form_class)
        from django.shortcuts import get_object_or_404
        from apps.core.models import Course
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        if course.custom_reg_form and course.custom_reg_form.layout_type == 'FLEXIBLE':
            if 'cpf' in form.fields: form.fields['cpf'].required = False
            if 'email' in form.fields: form.fields['email'].required = False
            if 'birth_date' in form.fields: form.fields['birth_date'].required = False
        return form

    def form_valid(self, form):
        from django.shortcuts import get_object_or_404
        from django.http import HttpResponseRedirect
        from apps.core.models import Course
        from apps.registrations.models import Registration
        
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        is_flexible = course.custom_reg_form and course.custom_reg_form.layout_type == 'FLEXIBLE'
        
        if not is_flexible and Registration.objects.filter(cpf=form.instance.cpf, course=course).exists():
            form.add_error('cpf', 'Este CPF já está inscrito nesta turma/data deste evento.')
            return self.form_invalid(form)

        inscricao = form.save(commit=False)
        inscricao.course = course
        inscricao.course_name = course.name
        inscricao.course_date = course.start_date
        inscricao.course_workload = course.hours
        inscricao.is_requested = False
        inscricao.save()
        
        name_parts = inscricao.full_name.split() if inscricao.full_name else []
        first_name = name_parts[0] if name_parts else ""
        course_date_str = course.start_date.strftime('%d/%m/%Y') if course.start_date else ""

        self.request.session['success_message'] = (
            f"{first_name}, obrigado! Seus dados foram registrados e enviados ao responsável "
            f"pelo evento {course.name} a ser realizado em {course_date_str}. Bom evento para você! Até breve!"
        )
        self.object = inscricao
        return HttpResponseRedirect(self.get_success_url())

class RegistrationSuccessView(TemplateView):
    template_name = "registrations/registration_success.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["success_message"] = self.request.session.pop("success_message", "Ação processada com sucesso.")
        return context


class RecurringEventRegistrationView(CreateView):
    model = Registration
    form_class = RegistrationForm
    template_name = "registrations/recurring_event_form.html"
    success_url = reverse_lazy("registrations:registration_success")

    def dispatch(self, request, *args, **kwargs):
        from django.utils import timezone
        from apps.core.models import RecurringEvent
        self.recurring_event = get_object_or_404(RecurringEvent, slug=self.kwargs['slug'])
        now = timezone.now()
        if self.recurring_event.registration_start and now < self.recurring_event.registration_start:
            return render(request, "time_locked.html", {"action_type": "inscrição", "lock_state": "early", "target_date": self.recurring_event.registration_start}, status=403)
        if self.recurring_event.registration_end and now > self.recurring_event.registration_end:
            return render(request, "time_locked.html", {"action_type": "inscrição", "lock_state": "late", "target_date": self.recurring_event.registration_end}, status=403)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.recurring_event
        if self.recurring_event.custom_reg_form:
            context['dynamic_fields'] = self.recurring_event.custom_reg_form.fields.all().order_by('order')
        return context

    def form_valid(self, form):
        if Registration.objects.filter(cpf=form.instance.cpf, recurring_event=self.recurring_event).exists():
            form.add_error('cpf', 'Este CPF já está inscrito neste evento recorrente.')
            return self.form_invalid(form)
        inscricao = form.save(commit=False)
        inscricao.recurring_event = self.recurring_event
        inscricao.course_name = self.recurring_event.name
        inscricao.course_workload = self.recurring_event.hours
        inscricao.is_requested = False
        inscricao.save()

        if self.recurring_event.custom_reg_form:
            from apps.registrations.models import DynamicResponse
            for field in self.recurring_event.custom_reg_form.fields.all():
                val = self.request.POST.get(f'dynamic_field_{field.id}')
                if val: DynamicResponse.objects.create(registration=inscricao, field=field, value=val)

        name_parts = inscricao.full_name.split() if inscricao.full_name else []
        first_name = name_parts[0] if name_parts else ""
        self.request.session['success_message'] = f"{first_name}, obrigado! Seus dados foram registrados no evento {self.recurring_event.name}."
        self.object = inscricao
        return HttpResponseRedirect(self.get_success_url())

class RecurringEventCertificateView(CreateView):
    model = Registration
    form_class = RegistrationForm
    template_name = "registrations/recurring_cert_form.html"
    success_url = reverse_lazy("registrations:registration_success")

    def dispatch(self, request, *args, **kwargs):
        from django.utils import timezone
        from django.http import HttpResponseForbidden
        from apps.core.models import RecurringEvent
        self.recurring_event = get_object_or_404(RecurringEvent, slug=self.kwargs['slug'])
        if self.recurring_event.event_type == 'CUSTOM' or self.recurring_event.no_certificate:
            return HttpResponseForbidden("Este evento não emite certificado.")
        now = timezone.now()
        if self.recurring_event.certificate_start and now < self.recurring_event.certificate_start:
            return render(request, "time_locked.html", {"action_type": "solicitação", "lock_state": "early", "target_date": self.recurring_event.certificate_start}, status=403)
        if self.recurring_event.certificate_end and now > self.recurring_event.certificate_end:
            return render(request, "time_locked.html", {"action_type": "solicitação", "lock_state": "late", "target_date": self.recurring_event.certificate_end}, status=403)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.recurring_event
        if self.recurring_event.custom_cert_form:
            context['dynamic_fields'] = self.recurring_event.custom_cert_form.fields.all().order_by('order')
        return context

    def form_valid(self, form):
        cpf = form.cleaned_data.get('cpf')
        name_parts = form.cleaned_data.get('full_name', '').split()
        first_name = name_parts[0] if name_parts else ""

        reg = Registration.objects.filter(cpf=cpf, recurring_event=self.recurring_event).first()
        if not reg:
            form.add_error('cpf', f"{first_name}, seu CPF não consta como inscrito neste evento. Realize a inscrição primeiro.")
            return self.form_invalid(form)

        registered_name = " ".join(reg.full_name.split()).lower()
        input_name = " ".join(form.cleaned_data.get('full_name', '').split()).lower()
        if registered_name != input_name:
            form.add_error('full_name', 'O nome informado não corresponde ao participante cadastrado. Revise os dados.')
            return self.form_invalid(form)

        if self.recurring_event.global_passkey:
            user_pass = self.request.POST.get('global_passkey', '')
            if user_pass != self.recurring_event.global_passkey:
                form.add_error(None, 'A Chave de Acesso (Senha) do evento está incorreta. Solicite ao responsável.')
                return self.form_invalid(form)

        protected_fields = ['full_name', 'cpf', 'rg', 'birth_date']
        for field, value in form.cleaned_data.items():
            if field not in protected_fields and value:
                setattr(reg, field, value)

        if self.recurring_event.custom_cert_form:
            from apps.registrations.models import DynamicResponse
            for field in self.recurring_event.custom_cert_form.fields.all():
                val = self.request.POST.get(f'dynamic_field_{field.id}')
                if val: DynamicResponse.objects.update_or_create(registration=reg, field=field, defaults={'value': val})

        if self.recurring_event.nps_form:
            from apps.registrations.models import NPSResponse
            for key, value in self.request.POST.items():
                if key.startswith('nps_question_') and value:
                    try:
                        q_id = int(key.replace('nps_question_', ''))
                        q = self.recurring_event.nps_form.questions.filter(id=q_id).first()
                        if q:
                            defaults = {'answer_score': int(value)} if q.question_type == 'score' else {'answer_text': value}
                            NPSResponse.objects.update_or_create(registration=reg, question=q, defaults=defaults)
                    except ValueError:
                        pass

        from apps.certificates.tasks import issue_certificate_task
        reg.is_requested = True
        reg.save()

        if reg.has_met_attendance:
            if reg.status == 'pending':
                msg = f"{first_name}, seus dados foram confirmados! Você atingiu a frequência mínima ({self.recurring_event.min_frequency}%) e seu certificado está sendo gerado."
                issue_certificate_task.delay(str(reg.id))
            else:
                msg = f"{first_name}, você já solicitou o certificado. Verifique sua caixa de entrada ou SPAM."
        else:
            msg = f"{first_name}, sua solicitação foi registrada! A emissão só ocorrerá caso você atinja a frequência mínima exigida pelo evento ({self.recurring_event.min_frequency}%)."

        self.request.session['success_message'] = msg
        self.object = reg
        return HttpResponseRedirect(self.get_success_url())
        from apps.registrations.models import NPSResponse
        for key, value in self.request.POST.items():
                if key.startswith('nps_question_') and value:
                    try:
                        q_id = int(key.replace('nps_question_', ''))
                        q = self.recurring_event.nps_form.questions.filter(id=q_id).first()
                        if q:
                            defaults = {'answer_score': int(value)} if q.question_type == 'score' else {'answer_text': value}
                            NPSResponse.objects.update_or_create(registration=reg, question=q, defaults=defaults)
                    except ValueError:
                        pass

        from apps.certificates.tasks import issue_certificate_task
        reg.is_requested = True
        reg.save()

        if reg.has_met_attendance:
            if reg.status == 'pending':
                msg = f"{first_name}, seus dados foram confirmados! Você atingiu a frequência mínima ({self.recurring_event.min_frequency}%) e seu certificado está sendo gerado."
                issue_certificate_task.delay(str(reg.id))
            else:
                msg = f"{first_name}, você já solicitou o certificado. Verifique sua caixa de entrada ou SPAM."
        else:
            msg = f"{first_name}, sua solicitação foi registrada! A emissão só ocorrerá caso você atinja a frequência mínima exigida pelo evento ({self.recurring_event.min_frequency}%)."

        self.request.session['success_message'] = msg
        self.object = reg
        return HttpResponseRedirect(self.get_success_url())
