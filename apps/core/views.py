import uuid
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Company, Instructor, Course
from .forms import CompanyForm, InstructorForm, CourseForm


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


import uuid
import csv
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Company, Instructor, Course
from .forms import CompanyForm, InstructorForm, CourseForm


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
                course.course_date.strftime("%d/%m/%Y"),
                course.city,
                course.state,
                course.instructor.full_name if course.instructor else "N/A",
                f"{course.hours}h"
            ])

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["instructors"] = Instructor.objects.filter(
            company=self.request.user.profile.company
        )
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
        context["instructors"] = Instructor.objects.filter(
            company=self.request.user.profile.company, 
            active=True
        )
        return context
