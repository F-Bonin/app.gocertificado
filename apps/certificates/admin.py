from django.contrib import admin
from .models import Certificate
from apps.registrations.models import Registration


class CertificateInline(admin.StackedInline):
    model = Certificate
    readonly_fields = ("numeric_code", "pdf_file", "emitted_at", "email_sent", "whatsapp_sent")
    extra = 0


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = (
        "numeric_code", "get_participant", "get_course",
        "email_sent", "whatsapp_sent", "emitted_at"
    )
    list_filter = ("email_sent", "whatsapp_sent")
    search_fields = ("numeric_code", "registration__full_name", "registration__cpf")
    readonly_fields = ("numeric_code", "emitted_at")

    def get_participant(self, obj):
        return obj.registration.full_name
    get_participant.short_description = "Participante"

    def get_course(self, obj):
        return obj.registration.course_name
    get_course.short_description = "Treinamento"
