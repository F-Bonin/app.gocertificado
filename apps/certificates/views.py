"""
apps/certificates/views.py
Painel do responsável + verificação de autenticidade.
"""
import logging
import csv
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from apps.registrations.models import Registration
from apps.certificates.models import Certificate
from apps.certificates.tasks import issue_certificate_task

from urllib.parse import urlencode
from django.urls import reverse
from apps.certificates.forms import LinkGeneratorForm

logger = logging.getLogger(__name__)


@method_decorator(login_required, name="dispatch")
class LinkGeneratorView(View):
    """Gera um link de inscrição pré-preenchido com dados do treinamento."""
    template_name = "certificates/link_generator.html"

    def get(self, request):
        form = LinkGeneratorForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = LinkGeneratorForm(request.POST)
        if form.is_valid():
            # Coletar dados do form
            data = form.cleaned_data
            # Mapear IDs para instructor_id
            params = {
                "instructor_id": data["instructor"].pk,
                "course_name": data["course_name"],
                "city": data["city"],
                "state": data["state"],
                "course_date": data["course_date"].isoformat(),
                "course_workload": data["course_workload"],
            }
            # Construir URL completa
            base_url = request.build_absolute_uri(reverse("registrations:form"))
            full_url = f"{base_url}?{urlencode(params)}"
            
            return render(request, self.template_name, {
                "form": form,
                "generated_url": full_url
            })
        
        return render(request, self.template_name, {"form": form})


@method_decorator(login_required, name="dispatch")
class BulkIssueCertificateView(View):
    """Emite certificados em massa para registros filtrados e pendentes."""

    def post(self, request):
        # Filtros atuais vindos do GET (mesma lógica do painel)
        course = request.GET.get("course")
        
        # Multitenancy
        queryset = Registration.objects.filter(
            course__company=request.user.profile.company,
            status=Registration.Status.PENDING
        )
        
        if course:
            queryset = queryset.filter(course_name__icontains=course)
        
        # Filtra apenas quem tem curso vinculado
        queryset = queryset.exclude(course__isnull=True)
        
        total = queryset.count()
        if total == 0:
            messages.info(request, "Nenhum certificado pendente encontrado para os filtros selecionados.")
            return redirect("certificates:panel")

        for reg in queryset:
            issue_certificate_task.delay(str(reg.pk))

        messages.success(
            request, 
            f"Processamento em massa iniciado! {total} certificados entraram na fila."
        )
        return redirect("certificates:panel")


@method_decorator(login_required, name="dispatch")
class DashboardView(View):
    """Exibe métricas e estatísticas do sistema com isolamento SaaS."""
    template_name = "certificates/dashboard.html"

    def get(self, request):
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        
        # Multitenancy query base
        company = request.user.profile.company
        regs_base = Registration.objects.filter(course__company=company)
        certs_base = Certificate.objects.filter(registration__course__company=company)

        # Mapeamento do dicionário de escolhas (choices) do Model
        status_choices_dict = dict(Registration.Status.choices)
        
        # Busca a distribuição e traduz os nomes em tempo de execução
        raw_status_distribution = regs_base.values('status').annotate(total=Count('id')).order_by('-total')
        distribuicao_status = []
        
        for item in raw_status_distribution:
            distribuicao_status.append({
                'label': status_choices_dict.get(item['status'], item['status']),
                'total': item['total'],
                'raw_status': item['status']  # Mantemos o valor original caso precise de lógica de cor no frontend
            })

        stats = {
            "total_registrations": regs_base.count(),
            "total_issued": certs_base.count(),
            "pending": regs_base.filter(status=Registration.Status.PENDING).count(),
            "issued_24h": certs_base.filter(emitted_at__gte=last_24h).count(),
            # Agrupamento por treinamento (Top 5)
            "top_courses": (
                regs_base.values("course__name")
                .annotate(total=Count("id"))
                .order_by("-total")[:5]
            ),
            # Agrupamento por status (Passaremos a versão traduzida)
            "status_dist": distribuicao_status
        }

        return render(request, self.template_name, {"stats": stats})


@method_decorator(login_required, name="dispatch")
class AdminPanelView(View):
    """Painel do responsável: lista participantes e permite emitir certificados."""
    template_name = "certificates/admin_panel.html"

    def get(self, request):
        company = request.user.profile.company
        registrations_list = (
            Registration.objects
            .select_related("course", "certificate")
            .filter(course__company=company)
            .order_by("-created_at")
        )
        # Filtros opcionais via query string
        course = request.GET.get("course")
        status = request.GET.get("status")
        if course:
            registrations_list = registrations_list.filter(course_name__icontains=course)
        if status:
            registrations_list = registrations_list.filter(status=status)

        # Paginação
        paginator = Paginator(registrations_list, 10)  # 10 por página
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context = {
            "registrations": page_obj,
            "status_choices": Registration.Status.choices,
            "filter_course": course or "",
            "filter_status": status or "",
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name="dispatch")
class SendCertificateView(View):
    """
    Acionado pelo botão "Enviar Certificado" no painel.
    Verifica se há instrutor vinculado e dispara a tarefa Celery.
    """

    def post(self, request, registration_id):
        # Multitenancy validation
        reg = get_object_or_404(
            Registration, 
            pk=registration_id, 
            course__company=request.user.profile.company
        )

        # Nota: Permitimos reenviar mesmo se já enviado (pela nova lógica da Fase 4)
        # Mas mantemos a proteção contra falta de curso
        if not reg.course:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"ok": False, "msg": "Vincule um curso antes de enviar."})
            messages.error(request, f"Vincule um curso a {reg.full_name} antes de emitir.")
            return redirect("certificates:panel")

        # Dispara tarefa assíncrona
        issue_certificate_task.delay(str(reg.pk))

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "msg": "Certificado sendo gerado e enviado!"})

        messages.success(
            request,
            f"Certificado de {reg.full_name} está sendo gerado e enviado!"
        )
        return redirect("certificates:panel")


@method_decorator(login_required, name="dispatch")
class ResetCertificateStatusView(View):
    """Retorna o status para Pendente e exclui o certificado para permitir nova emissão."""

    def post(self, request, registration_id):
        reg = get_object_or_404(
            Registration, 
            pk=registration_id, 
            course__company=request.user.profile.company
        )
        
        reg.status = Registration.Status.PENDING
        reg.save(update_fields=["status"])
        
        # Se já tiver um certificado, nós o excluímos para garantir uma nova geração limpa
        if hasattr(reg, "certificate"):
            reg.certificate.delete()
            
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "msg": f"Status de {reg.full_name} alterado para Pendente e certificado resetado."})

        messages.success(request, f"Status de {reg.full_name} alterado para Pendente e certificado resetado.")
        return redirect("certificates:panel")


@method_decorator(login_required, name="dispatch")
class DeleteRegistrationView(View):
    """Exclui uma inscrição e seu certificado associado (via cascata)."""

    def post(self, request, registration_id):
        from apps.registrations.models import Registration
        # Multitenancy validation
        reg = get_object_or_404(
            Registration, 
            pk=registration_id, 
            course__company=request.user.profile.company
        )
        reg.delete() # Isso apagará em cascata o Certificate associado
        
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "msg": "Excluído com sucesso."})
        
        messages.success(request, "Inscrição excluída com sucesso.")
        return redirect("certificates:panel")


@method_decorator(login_required, name="dispatch")
class ExportRegistrationsCSVView(View):
    """Gera um arquivo CSV com os participantes filtrados."""

    def get(self, request):
        # Multitenancy
        queryset = (
            Registration.objects
            .select_related("course")
            .filter(course__company=request.user.profile.company)
            .order_by("-created_at")
        )

        # Aplica os mesmos filtros do painel
        course = request.GET.get("course")
        status = request.GET.get("status")
        if course:
            queryset = queryset.filter(course_name__icontains=course)
        if status:
            queryset = queryset.filter(status=status)

        # Configura a resposta HTTP para CSV
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="participantes.csv"'

        # Escreve o BOM (Byte Order Mark) para compatibilidade com Excel
        response.write("\ufeff")

        writer = csv.writer(response, delimiter=";", quoting=csv.QUOTE_ALL)
        writer.writerow([
            "Nome Completo", "CPF", "E-mail", "WhatsApp",
            "Curso", "Data do Curso", "Carga Horária",
            "Status", "Instrutor"
        ])

        for reg in queryset:
            writer.writerow([
                reg.full_name,
                reg.cpf,
                reg.email,
                reg.whatsapp,
                reg.course_name,
                reg.course_date.strftime("%d/%m/%Y") if reg.course_date else "",
                f"{reg.course_workload}h",
                reg.get_status_display(),
                reg.course.signature_1.full_name if reg.course and reg.course.signature_1 else "Não atribuído"
            ])

        return response


class VerifyCertificateView(View):
    """Verificação pública de autenticidade do certificado."""
    template_name = "certificates/verify.html"

    def get(self, request, numeric_code=None):
        context = {"searched": False, "certificate": None, "not_found": False}

        code = numeric_code or request.GET.get("code", "").replace(" ", "")
        if code:
            context["searched"] = True
            try:
                cert = Certificate.objects.select_related(
                    "registration__course__company",
                    "registration__course__signature_1"
                ).get(numeric_code=code)
                context["certificate"] = cert
            except Certificate.DoesNotExist:
                context["not_found"] = True

        return render(request, self.template_name, context)


@method_decorator(login_required, name="dispatch")
class ParticipantListView(View):
    """Listagem de participantes únicos com estatísticas de treinamentos."""
    template_name = "certificates/participant_list.html"

    def get(self, request):
        profile = getattr(request.user, 'profile', None)
        company = profile.company if profile else None

        # Trava de segurança (Multi-tenancy) mantida. Ordenação por CPF obrigatória.
        qs = Registration.objects.select_related('course', 'certificate').filter(
            course__company=company
        ).order_by('cpf', '-course__start_date')

        q_name = request.GET.get("name", "")
        q_cpf = request.GET.get("cpf", "")
        q_course = request.GET.get("course", "")

        if q_name:
            qs = qs.filter(full_name__icontains=q_name)
        if q_cpf:
            qs = qs.filter(cpf__icontains=q_cpf)
        if q_course:
            qs = qs.filter(course__name__icontains=q_course)

        return render(request, self.template_name, {
            "registrations": qs,
            "q_name": q_name,
            "q_cpf": q_cpf,
            "q_course": q_course,
        })


@method_decorator(login_required, name="dispatch")
class ExportParticipantsCSVView(View):
    """Gera um CSV consolidado de todos os participantes únicos da empresa."""

    def get(self, request):
        company = request.user.profile.company
        
        # Busca todas as inscrições da empresa
        queryset = Registration.objects.filter(
            course__company=company
        ).select_related('course').order_by('full_name')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="alunos_exportados.csv"'
        
        # BOM para Excel reconhecer UTF-8
        response.write('\ufeff')
        
        writer = csv.writer(response, delimiter=';')
        writer.writerow(['Nome', 'CPF', 'Email', 'WhatsApp', 'Treinamento', 'Data', 'Status'])

        for reg in queryset:
            writer.writerow([
                reg.full_name,
                reg.cpf,
                reg.email,
                reg.whatsapp,
                reg.course.name if reg.course else "N/A",
                reg.course.start_date.strftime('%d/%m/%Y') if reg.course else "N/A",
                reg.get_status_display()
            ])

        return response


@method_decorator(login_required, name="dispatch")
class BulkSendCertificatesView(View):
    """Emite certificados em massa via AJAX para os registros filtrados e pendentes."""
    def post(self, request):
        profile = getattr(request.user, 'profile', None)
        company = profile.company if profile else None

        # Pega o filtro de curso atual que o usuário digitou na tela
        q_course = request.POST.get('course', '').strip()

        # Trava de segurança (Multi-tenancy) e Status Pendente
        qs = Registration.objects.filter(
            course__company=company,
            status=Registration.Status.PENDING
        )

        # Se o usuário filtrou por um treinamento específico na tela, aplicamos aqui também
        if q_course:
            qs = qs.filter(course__name__icontains=q_course)

        count = 0
        for reg in qs:
            # Dispara a tarefa assíncrona para o Celery processar no fundo
            issue_certificate_task.delay(str(reg.pk))
            count += 1

        return JsonResponse({
            "ok": True, 
            "msg": f"🚀 {count} certificados foram enviados para a fila de processamento! Eles serão emitidos em segundo plano."
        })


@method_decorator(login_required, name="dispatch")
class CheckRegistrationStatusView(View):
    """Retorna o status atual de uma lista de inscrições para atualização em tempo real."""
    def get(self, request):
        ids_str = request.GET.get('ids', '')
        if not ids_str:
            return JsonResponse({"statuses": {}})
        
        # Pega os IDs enviados pelo JavaScript e busca o status atual no banco
        ids_list = [id.strip() for id in ids_str.split(',') if id.strip()]
        qs = Registration.objects.filter(pk__in=ids_list).values('pk', 'status')
        
        # Retorna um dicionário { "id_1": "sent", "id_2": "pending" }
        statuses = {str(item['pk']): item['status'] for item in qs}
        return JsonResponse({"statuses": statuses})
