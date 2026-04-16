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
    ToggleRegistrationLinkView,
    ToggleCertificateLinkView,
    EventPresenceListView,
    TogglePresenceView,
    clone_course,
    generate_course_link,
    CourseLinkGeneratorView,
    CertificateDesignView,
    CertificatePreviewView,
    CertificateTemplateDeleteView,
    PublicCheckinView,
    ResetCheckinHashView,
    ToggleMassPresenceView,
    NPSFormListView,
    NPSFormCreateView,
    NPSFormUpdateView,
    NPSFormDeleteView,
    NPSQuestionCreateView,
    NPSQuestionDeleteView,
)

app_name = "core"

urlpatterns = [
    path("", CompanyUpdateView.as_view(), name="company_edit"),
    path("empresa/modelo-certificado/", CertificateDesignView.as_view(), name="certificate_design"),
    path("empresa/modelo-certificado/preview/", CertificatePreviewView.as_view(), name="certificate_preview"),
    path("empresa/modelo-certificado/<int:pk>/excluir/", CertificateTemplateDeleteView.as_view(), name="template_delete"),
    path("treinamentos/<int:pk>/reset-checkin/", ResetCheckinHashView.as_view(), name="reset_checkin_hash"),
    
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
    path("treinamentos/<int:pk>/toggle-registration/", ToggleRegistrationLinkView.as_view(), name="toggle_registration"),
    path("treinamentos/<int:pk>/toggle-certificate/", ToggleCertificateLinkView.as_view(), name="toggle_certificate"),
    path("treinamentos/<int:pk>/presenca/", EventPresenceListView.as_view(), name="course_presence"),
    path("inscricao/<uuid:reg_id>/toggle-presenca/", TogglePresenceView.as_view(), name="toggle_presence"),
    
    # NPS
    path("nps/", NPSFormListView.as_view(), name="nps_form_list"),
    path("nps/novo/", NPSFormCreateView.as_view(), name="nps_form_create"),
    path("nps/<int:pk>/editar/", NPSFormUpdateView.as_view(), name="nps_form_update"),
    path("nps/<int:pk>/excluir/", NPSFormDeleteView.as_view(), name="nps_form_delete"),
    path("nps/<int:nps_form_id>/pergunta/nova/", NPSQuestionCreateView.as_view(), name="nps_question_create"),
    path("nps/pergunta/<int:pk>/excluir/", NPSQuestionDeleteView.as_view(), name="nps_question_delete"),
    
    # Utilitários
    path("treinamentos/gerador/", CourseLinkGeneratorView.as_view(), name="course_link_generator"),
]
