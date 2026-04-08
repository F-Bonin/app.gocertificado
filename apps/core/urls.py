from django.urls import path
from .views import (
    CompanyUpdateView,
    InstructorListView,
    InstructorCreateView,
    InstructorUpdateView,
    InstructorDeleteView,
    CourseListView,
    CourseCreateView,
    CourseUpdateView,
    CourseDeleteView,
    CourseToggleStatusView,
    clone_course,
    generate_course_link,
    CourseLinkGeneratorView,
    CertificateDesignView,
    CertificatePreviewView,
)

app_name = "core"

urlpatterns = [
    path("", CompanyUpdateView.as_view(), name="company_edit"),
    path("empresa/modelo-certificado/", CertificateDesignView.as_view(), name="certificate_design"),
    path("empresa/modelo-certificado/preview/", CertificatePreviewView.as_view(), name="certificate_preview"),
    
    # Instrutores
    path("instrutores/", InstructorListView.as_view(), name="instructor_list"),
    path("instrutores/novo/", InstructorCreateView.as_view(), name="instructor_create"),
    path("instrutores/<int:pk>/editar/", InstructorUpdateView.as_view(), name="instructor_update"),
    path("instrutores/<int:pk>/excluir/", InstructorDeleteView.as_view(), name="instructor_delete"),
    
    # Treinamentos (Courses)
    path("treinamentos/", CourseListView.as_view(), name="course_list"),
    path("treinamentos/novo/", CourseCreateView.as_view(), name="course_create"),
    path("treinamentos/<int:pk>/editar/", CourseUpdateView.as_view(), name="course_update"),
    path("treinamentos/<int:pk>/excluir/", CourseDeleteView.as_view(), name="course_delete"),
    path("treinamentos/<int:pk>/clonar/", clone_course, name="course_clone"),
    path("treinamentos/<int:pk>/gerar-link/", generate_course_link, name="course_generate_link"),
    path("treinamentos/<int:pk>/toggle/", CourseToggleStatusView.as_view(), name="course_toggle"),
    
    # Utilitários
    path("treinamentos/gerador/", CourseLinkGeneratorView.as_view(), name="course_link_generator"),
]
