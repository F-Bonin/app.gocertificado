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
        """Define dinamicamente o template baseado na presença de formulário customizado."""
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        if course.custom_cert_form:
            return ["registrations/form_custom.html"]
        return ["registrations/form.html"]

    def form_valid(self, form):
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        cpf = form.cleaned_data.get('cpf')
        
        # Sênior Fix: Extrai apenas o primeiro nome como string (corrige bug de exibição de lista)
        name_parts = form.cleaned_data.get('full_name', '').split()
        first_name = name_parts[0] if name_parts else ""
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

        # Sênior Fix: Trava Anti-Fraude (Normalização rigorosa de strings removendo espaços duplos e capitalização)
        registered_name = " ".join(reg.full_name.split()).lower()
        input_name = " ".join(form.cleaned_data.get('full_name', '').split()).lower()
        
        if registered_name != input_name:
            form.add_error('full_name', 'O nome informado não corresponde ao participante cadastrado com este CPF. Por motivos de segurança, a solicitação foi bloqueada. Revise os dados ou contate o responsável do evento.')
            return self.form_invalid(form)

        # Sênior Fix: Validação de 2º Fator (Data de Nascimento)
        # Se o registro original possui data de nascimento, ela deve bater com a informada.
        input_birth_date = form.cleaned_data.get('birth_date')
        if reg.birth_date and input_birth_date and reg.birth_date != input_birth_date:
            form.add_error('birth_date', 'A data de nascimento informada não confere com o cadastro original. Por motivos de segurança, a solicitação foi bloqueada.')
            return self.form_invalid(form)

        # Atualiza apenas dados secundários de contato/endereço. Blinda a identidade core.
        # Sênior Fix: Liberado o campo 'email' para permitir que o aluno corrija erros de digitação do pré-evento.
        protected_fields = ['full_name', 'cpf', 'rg', 'birth_date']
        for field, value in form.cleaned_data.items():
            if field not in protected_fields and value:
                setattr(reg, field, value)
        
        # Salvamento das Respostas Dinâmicas (EAV Injection via contexto e recuperação via POST iterativo)
        for key, value in self.request.POST.items():
            if key.startswith('dynamic_field_') and value:
                try:
                    field_id = int(key.replace('dynamic_field_', ''))
                    field = DynamicField.objects.get(id=field_id)
                    DynamicResponse.objects.update_or_create(
                        registration=reg,
                        field=field,
                        defaults={'value': value}
                    )
                except (ValueError, DynamicField.DoesNotExist):
                    # Ignora erros de conversão ou campos inexistentes (blindagem anti-forging)
                    pass

        # Lógica para salvar o NPS
        if course.nps_form:
            from apps.registrations.models import NPSResponse
            from apps.core.models import NPSQuestion
            
            for key, value in self.request.POST.items():
                if key.startswith('nps_question_') and value:
                    try:
                        # Sênior Fix: Conversão segura do ID da pergunta
                        question_id = int(key.replace('nps_question_', ''))
                        
                        # Sênior Fix (Anti-Forging): Utilizamos .get() em vez de .filter().first()
                        # para que o sistema dispare DoesNotExist caso o usuário tente forjar
                        # uma resposta para uma pergunta que não pertence a este formulário ou não existe.
                        question = course.nps_form.questions.get(id=question_id)
                        
                        defaults = {}
                        if question.question_type == 'score':
                            try:
                                defaults['answer_score'] = int(value)
                            except ValueError:
                                # Se o valor do score não for numérico, ignoramos o preenchimento desse campo
                                pass
                        else:
                            defaults['answer_text'] = value
                            
                        # Persistência inteligente: cria ou atualiza a resposta vinculada ao participante
                        NPSResponse.objects.update_or_create(
                            registration=reg,
                            question=question,
                            defaults=defaults
                        )
                    except (ValueError, NPSQuestion.DoesNotExist):
                        # Blindagem de Segurança: Se o ID for forjado ou inválido, apenas ignoramos.
                        # Isso impede que o sistema retorne um erro 500 para o usuário final,
                        # garantindo robustez em arquiteturas expostas.
                        pass

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
        self.object = reg 
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        """
        Sênior Fix: Recupera o Treinamento no banco de dados via slug da URL
        e injeta no contexto do template para popular os dados visuais do evento
        (Nome, Data, Carga Horária, Local).
        Também injeta os campos dinâmicos personalizados (EAV Injection).
        """
        context = super().get_context_data(**kwargs)
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        context['course'] = course
        
        # Identifica se o formulário atual é para Inscrição ou Solicitação de Certificado
        dynamic_form = None
        if isinstance(self, EventRegistrationCreateView):
            dynamic_form = course.custom_reg_form
        else:
            dynamic_form = course.custom_cert_form
            
        if dynamic_form:
            context['dynamic_fields'] = dynamic_form.fields.all().order_by('order')
            
        return context

class EventRegistrationCreateView(RegistrationCreateView):
    """Exibe e processa o formulário de Inscrição (PRÉ-EVENTO)."""
    template_name = "registrations/event_form.html"

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

    def get_form_kwargs(self):
        """Injeta o objeto curso e sinaliza que NÃO é uma solicitação de certificado."""
        kwargs = super(RegistrationCreateView, self).get_form_kwargs()
        kwargs['course'] = get_object_or_404(Course, slug=self.kwargs['slug'])
        kwargs['is_cert_request'] = False
        return kwargs

    def get_template_names(self):
        """Define dinamicamente o template baseado na presença de formulário customizado de inscrição."""
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        if course.custom_reg_form:
            return ["registrations/event_form_custom.html"]
        return ["registrations/event_form.html"]

    def form_valid(self, form):
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        
        cpf_input = form.cleaned_data.get('cpf')
        if Registration.objects.filter(cpf=cpf_input, course=course).exists():
            full_name = form.cleaned_data.get('full_name') or ''
            first_name = full_name.split()[0] if full_name else "Participante"
            course_date_str = course.start_date.strftime('%d/%m/%Y') if course.start_date else ""
            
            # Sênior Fix: Desacoplamento da Mensagem Contextual
            # Em vez de injetar a mensagem longa diretamente no erro do campo (que polui a UI),
            # passamos um erro curto para o Django e injetamos a mensagem completa em uma flag.
            # Esta flag 'duplicate_error' servirá de gatilho para a abertura automática do 
            # Modal Extravagante no frontend, melhorando drasticamente a UX de interrupção.
            msg = f"{first_name}, você já se inscreveu para o evento {course.name} que será realizado em {course_date_str}. Caso esteja com dúvidas ou precise de mais informações, por favor, entre em contato com o responsável pelo evento. Obrigado."
            form.add_error('cpf', 'CPF já cadastrado neste evento.')
            form.duplicate_error = msg
            return self.form_invalid(form)

        inscricao = form.save(commit=False)
        inscricao.course = course
        inscricao.course_name = course.name
        inscricao.course_date = course.start_date
        inscricao.course_workload = course.hours
        inscricao.is_requested = False
        inscricao.save()
        
        # Salvamento das Respostas Dinâmicas (EAV Injection via contexto e recuperação via POST iterativo)
        for key, value in self.request.POST.items():
            if key.startswith('dynamic_field_') and value:
                try:
                    field_id = int(key.replace('dynamic_field_', ''))
                    field = DynamicField.objects.get(id=field_id)
                    DynamicResponse.objects.create(
                        registration=inscricao,
                        field=field,
                        value=value
                    )
                except (ValueError, DynamicField.DoesNotExist):
                    pass

        name_parts = inscricao.full_name.split() if inscricao.full_name else []
        first_name = name_parts[0] if name_parts else ""
        course_date_str = course.start_date.strftime('%d/%m/%Y') if course.start_date else ""

        # REGRA 0
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
