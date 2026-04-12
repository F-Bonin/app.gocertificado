import io
import uuid
import csv
from django.http import FileResponse, HttpResponse, JsonResponse
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
        template_form = CertificateTemplateForm()
        modelos_salvos = CertificateTemplate.objects.filter(company=company).order_by('-created_at')
        
        return render(request, self.template_name, {
            'form': form,
            'template_form': template_form,
            'modelos_salvos': modelos_salvos
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
                
        elif acao == 'save_selection':
            # Mantém a persistência da escolha do modelo ativo
            model_id = request.POST.get('certificate_model')
            company.certificate_model = model_id
            company.save(update_fields=['certificate_model'])
            messages.success(request, "Modelo de certificado ativo atualizado!")
            
        elif acao == 'save_template':
            template_form = CertificateTemplateForm(request.POST, request.FILES)
            if template_form.is_valid():
                novo_template = template_form.save(commit=False)
                novo_template.company = company
                novo_template.save()
                messages.success(request, f"Novo modelo '{novo_template.name}' criado com sucesso!")
            else:
                messages.error(request, "Erro ao criar novo modelo personalizado.")

        return redirect('core:certificate_design')


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