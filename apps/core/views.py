import io
import uuid
import csv
import json
from django.db.models import Q
from django.http import FileResponse, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import localtime

from apps.accounts.mixins import RoleRequiredMixin
from apps.certificates.services.pdf_generator import generate_preview_pdf
from apps.certificates.models import CertificateTemplate
from apps.certificates.tasks import issue_certificate_task
from apps.registrations.models import Registration
from .models import Company, Instructor, Course, NPSForm, NPSQuestion, DynamicForm, RecurringEvent, EventSession
from .forms import (
    CompanyForm, InstructorForm, CourseForm,
    CertificateDesignForm, CertificateTemplateForm,
    NPSFormModelForm, NPSQuestionForm, DynamicFormModelForm, DynamicFieldFormSet,
    RecurringEventForm, EventSessionFormSet
)

class CompanyUpdateView(RoleRequiredMixin, UpdateView):
    required_role = 'perm_company'
    model = Company
    form_class = CompanyForm
    template_name = "core/company_form.html"
    success_url = reverse_lazy("core:company_edit")

    def get_object(self, queryset=None):
        return self.request.user.profile.company

    def form_valid(self, form):
        messages.success(self.request, "Dados da empresa atualizados com sucesso!")
        return super().form_valid(form)


class InstructorListView(RoleRequiredMixin, ListView):
    required_role = 'perm_instructors'
    model = Instructor
    template_name = "core/instructor_list.html"
    context_object_name = "instructors"

    def get_queryset(self):
        return Instructor.objects.filter(company=self.request.user.profile.company)


class InstructorCreateView(RoleRequiredMixin, CreateView):
    required_role = 'perm_instructors'
    model = Instructor
    form_class = InstructorForm
    template_name = "core/instructor_form.html"
    success_url = reverse_lazy("core:instructor_list")

    def form_valid(self, form):
        form.instance.company = self.request.user.profile.company
        messages.success(self.request, "Instrutor cadastrado com sucesso!")
        return super().form_valid(form)


class InstructorUpdateView(RoleRequiredMixin, UpdateView):
    required_role = 'perm_instructors'
    model = Instructor
    form_class = InstructorForm
    template_name = "core/instructor_form.html"
    success_url = reverse_lazy("core:instructor_list")

    def get_queryset(self):
        return Instructor.objects.filter(company=self.request.user.profile.company)

    def form_valid(self, form):
        messages.success(self.request, "Dados do instrutor atualizados!")
        return super().form_valid(form)


class InstructorDeleteView(RoleRequiredMixin, DeleteView):
    required_role = 'perm_instructors'
    model = Instructor
    template_name = "core/instructor_confirm_delete.html"
    success_url = reverse_lazy("core:instructor_list")

    def get_queryset(self):
        return Instructor.objects.filter(company=self.request.user.profile.company)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Instrutor removido com sucesso.")
        return super().delete(request, *args, **kwargs)


class CourseListView(RoleRequiredMixin, ListView):
    required_role = 'perm_my_events'
    model = Course
    template_name = "core/course_list.html"
    context_object_name = "courses"

    def get_queryset(self):
        queryset = Course.objects.filter(
            company=self.request.user.profile.company
        ).order_by("-created_at")

        name = self.request.GET.get("name")
        date = self.request.GET.get("date")
        instructor = self.request.GET.get("instructor")

        if name:
            queryset = queryset.filter(name__icontains=name)
        if date:
            queryset = queryset.filter(start_date=date)
        if instructor:
            queryset = queryset.filter(Q(signature_1_id=instructor) | Q(signature_2_id=instructor) | Q(signature_3_id=instructor))
        return queryset

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get("export") == "csv":
            return self.export_csv(context["object_list"])
        return super().render_to_response(context, **response_kwargs)

    def export_csv(self, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="meus_treinamentos.csv"'
        response.write("\ufeff".encode("utf8"))
        writer = csv.writer(response, delimiter=";")
        writer.writerow(["Nome", "Data de Inicio", "Local", "Estado", "Carga Horária"])

        for course in queryset:
            writer.writerow([
                course.name,
                course.start_date.strftime("%d/%m/%Y") if course.start_date else "N/A",
                course.institution_name or course.city,
                course.state,
                f"{course.hours}h"
            ])
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["instructors"] = Instructor.objects.filter(company=self.request.user.profile.company)
        context["now"] = timezone.now()
        return context


class CourseCreateView(RoleRequiredMixin, CreateView):
    required_role = 'perm_standard_events'
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


class CourseUpdateView(RoleRequiredMixin, UpdateView):
    required_role = 'perm_my_events'
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


class CourseDeleteView(RoleRequiredMixin, DeleteView):
    required_role = 'perm_my_events'
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
    course = get_object_or_404(Course, pk=pk, company=request.user.profile.company)
    course.pk = None
    course.link_hash = uuid.uuid4()
    course.checkin_hash = uuid.uuid4()
    course.slug = None
    course.name = f"{course.name} (Cópia)"
    course.save()
    messages.success(request, "Treinamento clonado com sucesso!")
    return redirect("core:course_list")


@login_required
def generate_course_link(request, pk):
    course = get_object_or_404(Course, pk=pk, company=request.user.profile.company)
    course.link_hash = uuid.uuid4()
    course.save()
    messages.success(request, "Novo link gerado com sucesso!")
    return redirect("core:course_list")


class CourseLinkGeneratorView(RoleRequiredMixin, TemplateView):
    required_role = 'perm_my_events'
    template_name = "core/course_link_generator.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["courses"] = Course.objects.filter(
            company=self.request.user.profile.company,
            link_hash__isnull=False
        ).order_by("-start_date")
        return context
class CertificateDesignView(RoleRequiredMixin, View):
    required_role = 'perm_cert_design'
    template_name = 'core/certificate_design.html'

    def get(self, request):
        company = request.user.profile.company
        form = CertificateDesignForm(instance=company)
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


class CertificateTemplateDeleteView(RoleRequiredMixin, DeleteView):
    required_role = 'perm_cert_design'
    model = CertificateTemplate
    success_url = reverse_lazy("core:certificate_design")

    def get_queryset(self):
        return CertificateTemplate.objects.filter(company=self.request.user.profile.company)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Modelo personalizado removido com sucesso.")
        return super().delete(request, *args, **kwargs)


class CertificatePreviewView(RoleRequiredMixin, View):
    required_role = 'perm_cert_design'

    def get(self, request):
        model_type = request.GET.get('type', 'default')
        company = request.user.profile.company
        template = None
        if model_type == 'custom':
            template_id = request.GET.get('template_id')
            if template_id:
                template = CertificateTemplate.objects.filter(id=template_id, company=company).first()
            else:
                template = CertificateTemplate.objects.filter(company=company).order_by('-id').first()
            if not template:
                return HttpResponse("Nenhum modelo personalizado encontrado. Salve um modelo primeiro.", status=404)
        pdf_bytes = generate_preview_pdf(company, model_type, template)
        return HttpResponse(pdf_bytes, content_type='application/pdf')


class ToggleRegistrationLinkView(RoleRequiredMixin, View):
    required_role = 'perm_my_events'
    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk, company=self.request.user.profile.company)
        now = timezone.now()
        if course.registration_end and course.registration_end < now:
            course.registration_end = None
            messages.success(request, f"Inscrições para '{course.name}' reabertas com sucesso.")
        else:
            course.registration_end = now
            messages.warning(request, f"Inscrições para '{course.name}' encerradas.")
        course.save(update_fields=['registration_end'])
        return redirect('core:course_list')


class ToggleCertificateLinkView(RoleRequiredMixin, View):
    required_role = 'perm_my_events'
    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk, company=self.request.user.profile.company)
        now = timezone.now()
        cert_end = getattr(course, 'certificate_end', getattr(course, 'expires_at', None))
        if cert_end and cert_end < now:
            if hasattr(course, 'certificate_end'):
                course.certificate_end = None
            else:
                course.expires_at = None
            messages.success(request, f"Solicitações de certificado para '{course.name}' reabertas.")
        else:
            if hasattr(course, 'certificate_end'):
                course.certificate_end = now
            else:
                course.expires_at = now
            messages.warning(request, f"Solicitações de certificado para '{course.name}' encerradas.")
        
        update_fields = ['certificate_end'] if hasattr(course, 'certificate_end') else ['expires_at']
        course.save(update_fields=update_fields)
        return redirect('core:course_list')


class EventPresenceListView(RoleRequiredMixin, ListView):
    required_role = 'perm_my_events'
    model = Registration
    template_name = "core/presence_list.html"
    context_object_name = "registrations"

    def get_queryset(self):
        self.course = get_object_or_404(
            Course,
            pk=self.kwargs.get('pk'),
            company=self.request.user.profile.company
        )
        return self.course.registrations.all().order_by('full_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course
        context['now'] = timezone.now()
        return context


class TogglePresenceView(RoleRequiredMixin, View):
    required_role = 'perm_my_events'
    def post(self, request, reg_id):
        registration = get_object_or_404(
            Registration,
            id=reg_id,
            course__company=request.user.profile.company
        )
        registration.attended = not registration.attended
        registration.save(update_fields=['attended'])
        if registration.attended and registration.status == Registration.Status.PENDING and getattr(registration, 'is_requested', False):
            issue_certificate_task.delay(str(registration.id))
        return JsonResponse({"ok": True, "attended": registration.attended})


class ResetCheckinHashView(RoleRequiredMixin, View):
    required_role = 'perm_my_events'
    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk, company=request.user.profile.company)
        course.checkin_hash = uuid.uuid4()
        course.save(update_fields=['checkin_hash'])
        messages.success(request, f"O link de credenciamento de '{course.name}' foi resetado!")
        return redirect('core:course_list')


class PublicCheckinView(View):
    template_name = "core/public_checkin.html"
    def get(self, request, checkin_hash):
        try:
            course = Course.objects.get(checkin_hash=checkin_hash)
        except Course.DoesNotExist:
            return render(request, 'core/revoked_link.html', status=404)
        registrations = course.registrations.all().order_by('full_name')
        return render(request, self.template_name, {
            'course': course,
            'registrations': registrations
        })


@method_decorator(csrf_exempt, name='dispatch')
class ToggleMassPresenceView(View):
    def post(self, request, checkin_hash):
        course = get_object_or_404(Course, checkin_hash=checkin_hash)
        try:
            data = json.loads(request.body)
            action = data.get('action')
            new_status = True if action == 'check_all' else False
            now = timezone.now() if new_status else None
            
            registrations = course.registrations.all()
            registrations.update(attended=new_status, checkin_at=now)

            if new_status:
                for reg in registrations.filter(status='pending', is_requested=True):
                    issue_certificate_task.delay(str(reg.id))

            checkin_str = localtime(now).strftime('%d/%m/%y %H:%Mh') if now else ""
            return JsonResponse({"ok": True, "status": new_status, "checkin_time": checkin_str})
        except Exception as e:
            return JsonResponse({"ok": False, "error": str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class PublicTogglePresenceView(View):
    def post(self, request, reg_id):
        registration = get_object_or_404(Registration, id=reg_id)
        registration.attended = not registration.attended
        registration.checkin_at = timezone.now() if registration.attended else None
        registration.save(update_fields=['attended', 'checkin_at'])

        if registration.attended and registration.status == Registration.Status.PENDING and getattr(registration, 'is_requested', False):
            issue_certificate_task.delay(str(registration.id))

        checkin_str = localtime(registration.checkin_at).strftime('%d/%m/%y %H:%Mh') if registration.checkin_at else ""
        return JsonResponse({"ok": True, "attended": registration.attended, "checkin_time": checkin_str})


@method_decorator(csrf_exempt, name='dispatch')
class PublicSendLinkEmailView(View):
    def post(self, request, checkin_hash):
        from django.core.mail import send_mail
        from django.conf import settings
        
        course = get_object_or_404(Course, checkin_hash=checkin_hash)
        try:
            data = json.loads(request.body)
            email_destinatario = data.get('email')
            tipo_link = data.get('type')
            
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
class NPSFormListView(RoleRequiredMixin, ListView):
    required_role = 'perm_nps'
    model = NPSForm
    template_name = "core/nps_form_list.html"
    context_object_name = "nps_forms"

    def get_queryset(self):
        return NPSForm.objects.filter(company=self.request.user.profile.company).order_by("-created_at")

class NPSFormCreateView(RoleRequiredMixin, CreateView):
    required_role = 'perm_nps'
    model = NPSForm
    form_class = NPSFormModelForm
    template_name = "core/nps_form_form.html"
    success_url = reverse_lazy("core:nps_form_list")

    def form_valid(self, form):
        form.instance.company = self.request.user.profile.company
        messages.success(self.request, "Formulário NPS criado com sucesso!")
        return super().form_valid(form)

class NPSFormUpdateView(RoleRequiredMixin, UpdateView):
    required_role = 'perm_nps'
    model = NPSForm
    form_class = NPSFormModelForm
    template_name = "core/nps_form_form.html"
    success_url = reverse_lazy("core:nps_form_list")

    def get_queryset(self):
        return NPSForm.objects.filter(company=self.request.user.profile.company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question_form'] = NPSQuestionForm()
        context['questions'] = self.object.questions.all().order_by('order')
        return context

    def form_valid(self, form):
        messages.success(self.request, "Formulário NPS atualizado!")
        return super().form_valid(form)

class NPSFormDeleteView(RoleRequiredMixin, DeleteView):
    required_role = 'perm_nps'
    model = NPSForm
    template_name = "core/nps_form_confirm_delete.html"
    success_url = reverse_lazy("core:nps_form_list")

    def get_queryset(self):
        return NPSForm.objects.filter(company=self.request.user.profile.company)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Formulário NPS removido com sucesso.")
        return super().delete(request, *args, **kwargs)

class NPSQuestionCreateView(RoleRequiredMixin, CreateView):
    required_role = 'perm_nps'
    model = NPSQuestion
    form_class = NPSQuestionForm

    def form_valid(self, form):
        nps_form_id = self.kwargs.get('nps_form_id')
        nps_form = get_object_or_404(NPSForm, id=nps_form_id, company=self.request.user.profile.company)
        form.instance.nps_form = nps_form
        messages.success(self.request, "Pergunta adicionada com sucesso!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('core:nps_form_update', kwargs={'pk': self.kwargs.get('nps_form_id')})

class NPSQuestionDeleteView(RoleRequiredMixin, DeleteView):
    required_role = 'perm_nps'
    model = NPSQuestion

    def get_queryset(self):
        return NPSQuestion.objects.filter(nps_form__company=self.request.user.profile.company)

    def get_success_url(self):
        return reverse_lazy('core:nps_form_update', kwargs={'pk': self.object.nps_form.id})

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Pergunta removida.")
        return super().delete(request, *args, **kwargs)


# ==========================================
# GESTÃO EAV: FORMULÁRIOS DINÂMICOS
# ==========================================
class DynamicFormListView(RoleRequiredMixin, ListView):
    required_role = 'perm_custom_forms'
    model = DynamicForm
    template_name = "core/dynamic_form_list.html"
    context_object_name = "dynamic_forms"

    def get_queryset(self):
        return DynamicForm.objects.filter(company=self.request.user.profile.company).order_by("-created_at")

class DynamicFormCreateView(RoleRequiredMixin, CreateView):
    required_role = 'perm_custom_forms'
    model = DynamicForm
    form_class = DynamicFormModelForm
    template_name = "core/dynamic_form_form.html"
    success_url = reverse_lazy("core:dynamic_form_list")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['formset'] = DynamicFieldFormSet(self.request.POST)
        else:
            data['formset'] = DynamicFieldFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if form.is_valid() and formset.is_valid():
            form.instance.company = self.request.user.profile.company
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, "Formulário Dinâmico criado com sucesso!")
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form))

class DynamicFormUpdateView(RoleRequiredMixin, UpdateView):
    required_role = 'perm_custom_forms'
    model = DynamicForm
    form_class = DynamicFormModelForm
    template_name = "core/dynamic_form_form.html"
    success_url = reverse_lazy("core:dynamic_form_list")

    def get_queryset(self):
        return DynamicForm.objects.filter(company=self.request.user.profile.company)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['formset'] = DynamicFieldFormSet(self.request.POST, instance=self.object)
        else:
            data['formset'] = DynamicFieldFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, "Formulário Dinâmico atualizado com sucesso!")
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form))

class DynamicFormDeleteView(RoleRequiredMixin, DeleteView):
    required_role = 'perm_custom_forms'
    model = DynamicForm
    template_name = "core/dynamic_form_confirm_delete.html"
    success_url = reverse_lazy("core:dynamic_form_list")

    def get_queryset(self):
        return DynamicForm.objects.filter(company=self.request.user.profile.company)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Formulário removido com sucesso.")
        return super().delete(request, *args, **kwargs)


# ==========================================
# EVENTOS RECORRENTES (Sessões e Diários)
# ==========================================
class RecurringEventListView(RoleRequiredMixin, ListView):
    required_role = 'perm_my_events'
    model = RecurringEvent
    template_name = "core/recurring_event_list.html"
    context_object_name = "events"

    def get_queryset(self):
        return RecurringEvent.objects.filter(company=self.request.user.profile.company).order_by("-created_at")

class RecurringEventCreateView(RoleRequiredMixin, CreateView):
    required_role = 'perm_recurring_events'
    model = RecurringEvent
    form_class = RecurringEventForm
    template_name = "core/recurring_event_form.html"
    success_url = reverse_lazy("core:recurring_event_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.request.user.profile.company
        return kwargs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['formset'] = EventSessionFormSet(self.request.POST)
        else:
            data['formset'] = EventSessionFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if form.is_valid() and formset.is_valid():
            form.instance.company = self.request.user.profile.company
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, "Evento Recorrente criado com sucesso!")
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form))

class RecurringEventUpdateView(RoleRequiredMixin, UpdateView):
    required_role = 'perm_my_events'
    model = RecurringEvent
    form_class = RecurringEventForm
    template_name = "core/recurring_event_form.html"
    success_url = reverse_lazy("core:recurring_event_list")

    def get_queryset(self):
        return RecurringEvent.objects.filter(company=self.request.user.profile.company)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.request.user.profile.company
        return kwargs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['formset'] = EventSessionFormSet(self.request.POST, instance=self.object)
        else:
            data['formset'] = EventSessionFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, "Evento Recorrente atualizado com sucesso!")
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form))

class RecurringEventDeleteView(RoleRequiredMixin, DeleteView):
    required_role = 'perm_my_events'
    model = RecurringEvent
    template_name = "core/recurring_event_confirm_delete.html"
    success_url = reverse_lazy("core:recurring_event_list")

    def get_queryset(self):
        return RecurringEvent.objects.filter(company=self.request.user.profile.company)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Evento Recorrente removido com sucesso.")
        return super().delete(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class ToggleMassSessionPresenceView(View):
    def post(self, request, checkin_hash):
        session = get_object_or_404(EventSession, checkin_hash=checkin_hash)
        try:
            data = json.loads(request.body)
            action = data.get('action')
            new_status = True if action == 'check_all' else False
            now = timezone.now() if new_status else None
            
            from apps.registrations.models import SessionPresence
            for reg in session.recurring_event.registrations.all():
                pres, _ = SessionPresence.objects.get_or_create(registration=reg, session=session)
                pres.attended = new_status
                pres.checkin_at = now
                pres.save()

            checkin_str = localtime(now).strftime('%d/%m/%y %H:%Mh') if now else ""
            return JsonResponse({"ok": True, "status": new_status, "checkin_time": checkin_str})
        except Exception as e:
            return JsonResponse({"ok": False, "error": str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class ToggleSessionPresenceView(View):
    def post(self, request, session_id, reg_id):
        from apps.registrations.models import SessionPresence
        session = get_object_or_404(EventSession, id=session_id)
        reg = get_object_or_404(Registration, id=reg_id)
        
        pres, _ = SessionPresence.objects.get_or_create(registration=reg, session=session)
        pres.attended = not pres.attended
        pres.checkin_at = timezone.now() if pres.attended else None
        pres.save(update_fields=['attended', 'checkin_at'])

        checkin_str = localtime(pres.checkin_at).strftime('%d/%m/%y %H:%Mh') if pres.checkin_at else ""
        return JsonResponse({"ok": True, "attended": pres.attended, "checkin_time": checkin_str})


class ResetSessionCheckinHashView(RoleRequiredMixin, View):
    required_role = 'perm_my_events'
    def post(self, request, pk):
        session = get_object_or_404(EventSession, pk=pk, recurring_event__company=request.user.profile.company)
        session.checkin_hash = uuid.uuid4()
        session.save(update_fields=['checkin_hash'])
        messages.success(request, f"O link de credenciamento do encontro '{session.theme}' foi resetado!")
        return redirect('core:recurring_event_list')
    
class PublicSessionCheckinView(View):
    """View pública para credenciamento via Magic Link de uma Sessão específica (Evento Recorrente)."""
    template_name = "core/public_session_checkin.html"

    def get(self, request, checkin_hash):
        from django.shortcuts import render
        from django.db.models import Prefetch
        from apps.core.models import EventSession
        from apps.registrations.models import SessionPresence

        try:
            session = EventSession.objects.get(checkin_hash=checkin_hash)
        except EventSession.DoesNotExist:
            return render(request, 'core/revoked_link.html', status=404)

        course = session.recurring_event
        
        # Busca as inscrições e faz um "join" virtual inteligente (Prefetch) 
        # apenas com a presença desta sessão específica para exibição no HTML.
        registrations = course.registrations.prefetch_related(
            Prefetch(
                'session_presences',
                queryset=SessionPresence.objects.filter(session=session),
                to_attr='current_presence'
            )
        ).order_by('full_name')

        return render(request, self.template_name, {
            'course': course,
            'session': session,
            'registrations': registrations
        })    

@method_decorator(csrf_exempt, name='dispatch')
class PublicToggleSessionPresenceView(View):
    """View pública de check-in individual via AJAX para Sessões (Eventos Recorrentes)."""
    def post(self, request, session_id, reg_id):
        from django.shortcuts import get_object_or_404
        from django.http import JsonResponse
        from django.utils import timezone
        from django.utils.timezone import localtime
        from apps.core.models import EventSession
        from apps.registrations.models import Registration, SessionPresence

        session = get_object_or_404(EventSession, id=session_id)
        reg = get_object_or_404(Registration, id=reg_id)
        
        pres, _ = SessionPresence.objects.get_or_create(registration=reg, session=session)
        pres.attended = not pres.attended
        pres.checkin_at = timezone.now() if pres.attended else None
        pres.save(update_fields=['attended', 'checkin_at'])

        checkin_str = localtime(pres.checkin_at).strftime('%d/%m/%y %H:%Mh') if pres.checkin_at else ""
        return JsonResponse({"ok": True, "attended": pres.attended, "checkin_time": checkin_str})

class SessionPresenceListView(RoleRequiredMixin, ListView):
    """Lista de presença administrativa para uma Sessão (Evento Recorrente)."""
    required_role = 'perm_my_events'
    model = Registration
    template_name = "core/session_presence_list.html"
    context_object_name = "registrations"

    def get_queryset(self):
        from django.shortcuts import get_object_or_404
        from django.db.models import Prefetch
        from apps.core.models import EventSession
        from apps.registrations.models import SessionPresence

        self.session = get_object_or_404(
            EventSession,
            pk=self.kwargs.get('pk'),
            recurring_event__company=self.request.user.profile.company
        )

        # Busca as inscrições e faz um "join" virtual inteligente (Prefetch)
        # apenas com a presença desta sessão específica para exibição no HTML.
        return self.session.recurring_event.registrations.prefetch_related(
            Prefetch(
                'session_presences',
                queryset=SessionPresence.objects.filter(session=self.session),
                to_attr='current_presence'
            )
        ).order_by('full_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.utils import timezone
        context['session'] = self.session
        context['course'] = self.session.recurring_event
        context['now'] = timezone.now()
        return context