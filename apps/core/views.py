import io
import uuid
import csv
import json
from django.http import FileResponse, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.certificates.services.pdf_generator import generate_preview_pdf
from apps.certificates.models import CertificateTemplate
from apps.certificates.tasks import issue_certificate_task
from apps.registrations.models import Registration
from .models import Company, Instructor, Course
from .forms import (
    CompanyForm, InstructorForm, CourseForm, 
    CertificateDesignForm, CertificateTemplateForm
)


class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    """Edita os dados da empresa vinculada ao usuário logado."""
    model = Company
    form_class = CompanyForm
    template_name = "core/company_form.html"
    success_url = reverse_lazy("core:company_edit")

    def get_object(self, queryset=None):
        return self.request.user.profile.company

    def form_valid(self, form):
        messages.success(self.request, "Dados da empresa atualizados com sucesso!")
        return super().form_valid(form)


class InstructorListView(LoginRequiredMixin, ListView):
    """Lista instrutores da empresa do usuário."""
    model = Instructor
    template_name = "core/instructor_list.html"
    context_object_name = "instructors"

    def get_queryset(self):
        return Instructor.objects.filter(company=self.request.user.profile.company)


class InstructorCreateView(LoginRequiredMixin, CreateView):
    """Cria novo instrutor vinculado à empresa do usuário."""
    model = Instructor
    form_class = InstructorForm
    template_name = "core/instructor_form.html"
    success_url = reverse_lazy("core:instructor_list")

    def form_valid(self, form):
        form.instance.company = self.request.user.profile.company
        messages.success(self.request, "Instrutor cadastrado com sucesso!")
        return super().form_valid(form)


class InstructorUpdateView(LoginRequiredMixin, UpdateView):
    """Edita instrutor (apenas da empresa do usuário)."""
    model = Instructor
    form_class = InstructorForm
    template_name = "core/instructor_form.html"
    success_url = reverse_lazy("core:instructor_list")

    def get_queryset(self):
        return Instructor.objects.filter(company=self.request.user.profile.company)

    def form_valid(self, form):
        messages.success(self.request, "Dados do instrutor atualizados!")
        return super().form_valid(form)


class InstructorDeleteView(LoginRequiredMixin, DeleteView):
    """Exclui instrutor (apenas da empresa do usuário)."""
    model = Instructor
    template_name = "core/instructor_confirm_delete.html"
    success_url = reverse_lazy("core:instructor_list")

    def get_queryset(self):
        return Instructor.objects.filter(company=self.request.user.profile.company)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Instrutor removido com sucesso.")
        return super().delete(request, *args, **kwargs)


class CourseListView(LoginRequiredMixin, ListView):
    """Lista treinamentos da empresa do usuário com filtros e exportação CSV."""
    model = Course
    template_name = "core/course_list.html"
    context_object_name = "courses"

    def get_queryset(self):
        queryset = Course.objects.filter(
            company=self.request.user.profile.company
        ).order_by("-created_at")

        # Filtros via GET
        name = self.request.GET.get("name")
        date = self.request.GET.get("date")
        instructor = self.request.GET.get("instructor")

        if name:
            queryset = queryset.filter(name__icontains=name)
        if date:
            queryset = queryset.filter(course_date=date)
        if instructor:
            queryset = queryset.filter(instructor_id=instructor)

        return queryset

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get("export") == "csv":
            return self.export_csv(context["object_list"])
        return super().render_to_response(context, **response_kwargs)

    def export_csv(self, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="meus_treinamentos.csv"'
        response.write("\ufeff".encode("utf8"))  # BOM para Excel ler UTF-8

        writer = csv.writer(response)
        writer.writerow(["Nome", "Data", "Cidade", "Estado", "Instrutor", "Carga Horária"])

        for course in queryset:
            writer.writerow([
                course.name,
                course.course_date.strftime("%d/%m/%Y") if course.course_date else "N/A",
                course.city,
                course.state,
                course.instructor.full_name if course.instructor else "N/A",
                f"{course.hours}h"
            ])

        return response

    def get_context_data(self, **kwargs):
        from django.utils import timezone
        context = super().get_context_data(**kwargs)
        context["instructors"] = Instructor.objects.filter(
            company=self.request.user.profile.company
        )
        context["now"] = timezone.now()
        return context


class CourseCreateView(LoginRequiredMixin, CreateView):
    """Cria novo treinamento vinculado à empresa do usuário."""
    model = Course
    form_class = CourseForm
    template_name = "core/course_form.html"
    success_url = reverse_lazy("core:course_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.request.user.profile.company
        return kwargs

    def form_valid(self, form):
        form.instance.company = self.request.user.profile.company
        form.instance.link_hash = uuid.uuid4()
        messages.success(self.request, "Treinamento cadastrado com sucesso!")
        return super().form_valid(form)


class CourseUpdateView(LoginRequiredMixin, UpdateView):
    """Edita treinamento (apenas da empresa do usuário)."""
    model = Course
    form_class = CourseForm
    template_name = "core/course_form.html"
    success_url = reverse_lazy("core:course_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.request.user.profile.company
        return kwargs

    def get_queryset(self):
        return Course.objects.filter(company=self.request.user.profile.company)

    def form_valid(self, form):
        messages.success(self.request, "Treinamento atualizado!")
        return super().form_valid(form)


class CourseDeleteView(LoginRequiredMixin, DeleteView):
    """Exclui treinamento (apenas da empresa do usuário)."""
    model = Course
    template_name = "core/course_confirm_delete.html"
    success_url = reverse_lazy("core:course_list")

    def get_queryset(self):
        return Course.objects.filter(company=self.request.user.profile.company)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Treinamento removido com sucesso.")
        return super().delete(request, *args, **kwargs)


@login_required
def clone_course(request, pk):
    """Clona um treinamento existente."""
    course = get_object_or_404(Course, pk=pk, company=request.user.profile.company)
    course.pk = None
    course.link_hash = None  # Será gerado um novo se necessário ou no Create
    course.name = f"{course.name} (Cópia)"
    course.save()
    messages.success(request, "Treinamento clonado com sucesso!")
    return redirect("core:course_list")


@login_required
def generate_course_link(request, pk):
    """Gera um novo hash único para o link de inscrição do curso."""
    course = get_object_or_404(Course, pk=pk, company=request.user.profile.company)
    course.link_hash = uuid.uuid4()
    course.save()
    messages.success(request, "Novo link gerado com sucesso!")
    return redirect("core:course_list")


class CourseLinkGeneratorView(LoginRequiredMixin, TemplateView):
    """Tela para geração dinâmica de links de inscrição multitenant."""
    template_name = "core/course_link_generator.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Passa os treinamentos que já possuem link_hash gerado
        context["courses"] = Course.objects.filter(
            company=self.request.user.profile.company,
            link_hash__isnull=False
        ).order_by("-start_date")
        return context


class CertificateDesignView(LoginRequiredMixin, View):
    """Gerencia as configurações de design do certificado da empresa."""
    template_name = 'core/certificate_design.html'

    def get(self, request):
        company = request.user.profile.company
        form = CertificateDesignForm(instance=company)
        
        # Lógica de seleção de modelo para edição (CRUD)
        template_id = request.GET.get('edit_template')
        if template_id:
            instance = get_object_or_404(CertificateTemplate, id=template_id, company=company)
            template_form = CertificateTemplateForm(instance=instance)
        else:
            template_form = CertificateTemplateForm()

        modelos_salvos = CertificateTemplate.objects.filter(company=company).order_by('-created_at')
        
        return render(request, self.template_name, {
            'form': form,
            'template_form': template_form,
            'modelos_salvos': modelos_salvos,
            'editing_template': template_id
        })

    def post(self, request):
        company = request.user.profile.company
        acao = request.POST.get('action')
        
        if acao == 'save_logo':
            form = CertificateDesignForm(request.POST, request.FILES, instance=company)
            if form.is_valid():
                form.save()
                messages.success(request, "Logomarca atualizada com sucesso!")
            else:
                messages.error(request, "Erro ao salvar logomarca.")
                
        elif acao == 'save_template':
            # Busca instância se ID for passado (edição), senão cria (instancia vazia)
            template_id = request.POST.get('template_id')
            instance = None
            if template_id:
                instance = get_object_or_404(CertificateTemplate, id=template_id, company=company)
            
            template_form = CertificateTemplateForm(request.POST, request.FILES, instance=instance)
            if template_form.is_valid():
                novo_template = template_form.save(commit=False)
                novo_template.company = company
                novo_template.save()
                msg = f"Modelo '{novo_template.name}' atualizado!" if instance else f"Novo modelo '{novo_template.name}' criado!"
                messages.success(request, msg)
            else:
                messages.error(request, "Erro ao salvar modelo personalizado.")

        return redirect('core:certificate_design')


class CertificateTemplateDeleteView(LoginRequiredMixin, DeleteView):
    """Exclui um modelo personalizado da empresa."""
    model = CertificateTemplate
    success_url = reverse_lazy("core:certificate_design")

    def get_queryset(self):
        return CertificateTemplate.objects.filter(company=self.request.user.profile.company)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Modelo personalizado removido com sucesso.")
        return super().delete(request, *args, **kwargs)


class ToggleRegistrationLinkView(LoginRequiredMixin, View):
    """View para encerrar ou reabrir links de INSCRIÇÃO (Pré-Evento)."""
    def post(self, request, pk):
        from django.utils import timezone
        course = get_object_or_404(Course, pk=pk, company=self.request.user.profile.company)
        now = timezone.now()

        # Lógica de Inversão:
        # Se o término já passou (encerrado), reabre (None)
        if course.registration_end and course.registration_end < now:
            course.registration_end = None
            messages.success(request, f"Inscrições para '{course.name}' reabertas com sucesso.")
        # Se está ativo (None ou futuro), encerra (now)
        else:
            course.registration_end = now
            messages.warning(request, f"Inscrições para '{course.name}' encerradas.")

        course.save(update_fields=['registration_end'])
        return redirect('core:course_list')


class ToggleCertificateLinkView(LoginRequiredMixin, View):
    """View para encerrar ou reabrir links de SOLICITAÇÃO (Certificado)."""
    def post(self, request, pk):
        from django.utils import timezone
        course = get_object_or_404(Course, pk=pk, company=self.request.user.profile.company)
        now = timezone.now()

        # Lógica de Inversão:
        # Se o término já passou (encerrado), reabre (None)
        if course.certificate_end and course.certificate_end < now:
            course.certificate_end = None
            messages.success(request, f"Solicitações de certificado para '{course.name}' reabertas.")
        # Se está ativo (None ou futuro), encerra (now)
        else:
            course.certificate_end = now
            messages.warning(request, f"Solicitações de certificado para '{course.name}' encerradas.")

        course.save(update_fields=['certificate_end'])
        return redirect('core:course_list')


class CertificatePreviewView(LoginRequiredMixin, View):
    def get(self, request):
        model_type = request.GET.get('type', 'default')
        company = request.user.profile.company
        template = None

        # ==========================================
        # LÓGICA DO MODELO PERSONALIZADO
        # ==========================================
        if model_type == 'custom':
            template_id = request.GET.get('template_id')
            
            if template_id:
                template = CertificateTemplate.objects.filter(id=template_id, company=company).first()
            else:
                template = CertificateTemplate.objects.filter(company=company).order_by('-id').first()
                
            if not template:
                return HttpResponse("Nenhum modelo personalizado encontrado. Salve um modelo primeiro.", status=404)

        # ==========================================
        # CORREÇÃO SÊNIOR: EMPACOTANDO O PDF
        # ==========================================
        # 1. Geramos os bytes crus do arquivo PDF
        pdf_bytes = generate_preview_pdf(company, model_type, template)
        
        # 2. Empacotamos numa resposta HTTP válida para o navegador ler como PDF
        return HttpResponse(pdf_bytes, content_type='application/pdf')


class EventPresenceListView(LoginRequiredMixin, ListView):
    """
    Lista de presença de um evento específico.
    Exibe todos os participantes inscritos e permite realizar o check-in.
    """
    model = Registration
    template_name = "core/presence_list.html"
    context_object_name = "registrations"

    def get_queryset(self):
        # Validação Multi-tenant: Busca o curso garantindo que pertence à empresa do usuário
        self.course = get_object_or_404(
            Course, 
            pk=self.kwargs.get('pk'), 
            company=self.request.user.profile.company
        )
        # Retorna as inscrições vinculadas a este curso, ordenadas por nome
        return self.course.registrations.all().order_by('full_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Injeta o objeto course no contexto para exibição de cabeçalhos no template
        context['course'] = self.course
        return context


class TogglePresenceView(LoginRequiredMixin, View):
    """
    Lógica de Check-in via AJAX (Online).
    Inverte o status de 'attended' (presença) de um participante.
    Segurança Multi-tenant: Garante que a inscrição pertença a um curso da empresa do usuário.
    """
    def post(self, request, reg_id):
        # Recupera a inscrição validando o vínculo com a empresa do usuário logado
        registration = get_object_or_404(
            Registration, 
            id=reg_id, 
            course__company=request.user.profile.company
        )
        
        # Inverte o valor de attended (True vira False, e vice-versa)
        registration.attended = not registration.attended
        
        # Otimização: Salva apenas o campo alterado
        registration.save(update_fields=['attended'])
        
        # DISPARO AUTOMÁTICO (CELERY): Se o check-in foi habilitado e o aluno já possui 
        # uma solicitação de certificado pendente, dispara a emissão assíncrona imediatamente.
        if registration.attended and registration.status == Registration.Status.PENDING:
            issue_certificate_task.delay(str(registration.id))
        
        # Retorna resposta JSON para atualização reativa na interface (JS)
        return JsonResponse({
            "ok": True, 
            "attended": registration.attended
        })


class PublicCheckinView(View):
    """View pública para credenciamento via Magic Link (Hash)."""
    template_name = "core/public_checkin.html"

    def get(self, request, checkin_hash):
        from django.shortcuts import render
        from apps.core.models import Course
        
        try:
            course = Course.objects.get(checkin_hash=checkin_hash)
        except Course.DoesNotExist:
            return render(request, 'core/revoked_link.html', status=404)

        registrations = course.registrations.all().order_by('full_name')
        return render(request, self.template_name, {
            'course': course,
            'registrations': registrations
        })


class ResetCheckinHashView(LoginRequiredMixin, View):
    """Gera um novo Hash de Credenciamento para o curso, invalidando o anterior."""
    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk, company=request.user.profile.company)
        course.checkin_hash = uuid.uuid4()
        course.save(update_fields=['checkin_hash'])
        messages.success(request, f"O link de credenciamento de '{course.name}' foi resetado!")
        return redirect('core:course_list')


@method_decorator(csrf_exempt, name='dispatch')
class ToggleMassPresenceView(View):
    """
    Check-in em Massa via AJAX para o Painel Público.
    """
    def post(self, request, checkin_hash):
        from django.http import JsonResponse
        from django.shortcuts import get_object_or_404
        from apps.core.models import Course
        from apps.certificates.tasks import issue_certificate_task
        from django.utils import timezone
        from django.utils.timezone import localtime
        import json

        course = get_object_or_404(Course, checkin_hash=checkin_hash)
        try:
            data = json.loads(request.body)
            action = data.get('action')
            new_status = True if action == 'check_all' else False
            now = timezone.now() if new_status else None
            
            registrations = course.registrations.all()
            registrations.update(attended=new_status, checkin_at=now)

            if new_status:
                for reg in registrations.filter(status='pending'):
                    issue_certificate_task.delay(str(reg.id))

            # Sênior Fix: Converte UTC para a hora local (America/Sao_Paulo) antes de formatar a string
            checkin_str = localtime(now).strftime('%d/%m/%y %H:%Mh') if now else ""
            return JsonResponse({"ok": True, "status": new_status, "checkin_time": checkin_str})
        except Exception as e:
            return JsonResponse({"ok": False, "error": str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class PublicTogglePresenceView(View):
    """
    Check-in Individual via AJAX para o Painel Público.
    Protegido pelo ID da inscrição (UUID único).
    """
    def post(self, request, reg_id):
        from apps.registrations.models import Registration
        from django.shortcuts import get_object_or_404
        from django.http import JsonResponse
        from apps.certificates.tasks import issue_certificate_task
        from django.utils import timezone
        from django.utils.timezone import localtime
        
        registration = get_object_or_404(Registration, id=reg_id)
        
        registration.attended = not registration.attended
        registration.checkin_at = timezone.now() if registration.attended else None
        registration.save(update_fields=['attended', 'checkin_at'])
        
        if registration.attended and registration.status == Registration.Status.PENDING:
            issue_certificate_task.delay(str(registration.id))
            
        # Sênior Fix: Converte UTC para a hora local (America/Sao_Paulo) antes de formatar a string
        checkin_str = localtime(registration.checkin_at).strftime('%d/%m/%y %H:%Mh') if registration.checkin_at else ""
        return JsonResponse({"ok": True, "attended": registration.attended, "checkin_time": checkin_str})


@method_decorator(csrf_exempt, name='dispatch')
class PublicSendLinkEmailView(View):
    """
    Endpoint para envio rápido de links (Inscrição ou Certificado) via e-mail.
    Chamado pelo painel de credenciamento público.
    """
    def post(self, request, checkin_hash):
        from django.core.mail import send_mail
        from django.conf import settings
        
        course = get_object_or_404(Course, checkin_hash=checkin_hash)
        
        try:
            data = json.loads(request.body)
            email_destinatario = data.get('email')
            tipo_link = data.get('type') # 'inscricao' ou 'certificado'
            
            if not email_destinatario:
                return JsonResponse({"ok": False, "error": "E-mail não informado."}, status=400)

            link_inscricao = f"{request.scheme}://{request.get_host()}{course.get_registration_url()}"
            link_certificado = f"{request.scheme}://{request.get_host()}/solic-cert-{course.slug}/"
            
            subject = f"Links do Evento: {course.name}"
            message = f"Olá,\n\nConforme solicitado no credenciamento do evento '{course.name}', seguem os links de acesso:\n\n"
            
            if tipo_link == 'inscricao':
                message += f"Link para Inscrição: {link_inscricao}\n"
            elif tipo_link == 'certificado':
                message += f"Link para Solicitar Certificado: {link_certificado}\n"
            else:
                message += f"Link para Inscrição: {link_inscricao}\n"
                message += f"Link para Solicitar Certificado: {link_certificado}\n"

            message += f"\nAtenciosamente,\nEquipe {course.company.name}"

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email_destinatario],
                fail_silently=False,
            )
            
            return JsonResponse({"ok": True})
        except Exception as e:
            return JsonResponse({"ok": False, "error": str(e)}, status=400)