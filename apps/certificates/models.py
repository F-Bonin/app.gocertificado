"""
apps/certificates/models.py
Modelo do certificado gerado.
"""
import uuid
import secrets
from django.db import models
from apps.registrations.models import Registration


def _generate_numeric_code() -> str:
    """Gera código numérico único de 12 dígitos."""
    return "".join([str(secrets.randbelow(10)) for _ in range(12)])


class Certificate(models.Model):
    """Certificado emitido para um participante."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        related_name="certificate",
        verbose_name="Inscrição"
    )
    company = models.ForeignKey(
        'core.Company', 
        on_delete=models.CASCADE, 
        related_name='certificates',
        null=True, 
        blank=True,
        verbose_name="Empresa"
    )

    # Código de autenticidade
    numeric_code = models.CharField(
        "Código numérico",
        max_length=20,
        unique=True,
        default=_generate_numeric_code,
        editable=False
    )

    # Arquivo PDF
    pdf_file = models.FileField(
        "Arquivo PDF",
        upload_to="certificates/pdfs/",
        blank=True, null=True
    )

    # Controle de envio
    emitted_at = models.DateTimeField("Emitido em", auto_now_add=True)
    email_sent = models.BooleanField("E-mail enviado", default=False)
    email_sent_at = models.DateTimeField("E-mail enviado em", null=True, blank=True)
    whatsapp_sent = models.BooleanField("WhatsApp enviado", default=False)
    whatsapp_sent_at = models.DateTimeField("WhatsApp enviado em", null=True, blank=True)

    class Meta:
        verbose_name = "Certificado"
        verbose_name_plural = "Certificados"
        ordering = ["-emitted_at"]

    def __str__(self):
        return f"Cert. {self.numeric_code} — {self.registration.full_name}"

    @property
    def verification_url(self) -> str:
        from django.conf import settings
        from django.urls import reverse
        path = reverse("certificates:verify_direct", kwargs={"numeric_code": self.numeric_code})
        return f"{settings.CERTIFICATE_BASE_URL.rstrip('/')}{path}"

    @property
    def numeric_code_formatted(self) -> str:
        """Exibe código em grupos de 4: 1234 5678 9012"""
        c = self.numeric_code
        return f"{c[:4]} {c[4:8]} {c[8:]}"


class CertificateTemplate(models.Model):
    """Modelo para armazenar múltiplos modelos de certificados personalizados."""
    company = models.ForeignKey(
        'core.Company', 
        on_delete=models.CASCADE, 
        related_name='certificate_templates',
        verbose_name="Empresa"
    )
    name = models.CharField("Nome do Modelo", max_length=100, help_text="Ex: Modelo Padrão, Modelo Imersão")
    
    # Campos transferidos da configuração global (Company)
    background_image = models.ImageField(
        "Modelo de Certificado (A4 Paisagem)", 
        upload_to='company/templates/', 
        blank=True, null=True
    )
    title = models.CharField(
        "Título do Certificado", 
        max_length=80, 
        default="Certificado de Conclusão", 
        blank=True, null=True
    )
    text_1 = models.CharField(
        "Texto 1", 
        max_length=80, 
        default="Certificamos que", 
        blank=True, null=True
    )
    text_2 = models.CharField(
        "Texto 2", 
        max_length=80, 
        default="portador do CPF", 
        blank=True, null=True
    )
    text_3 = models.CharField(
        "Texto 3", 
        max_length=80, 
        default="concluiu com êxito o curso/treinamento", 
        blank=True, null=True
    )
    text_4 = models.CharField(
        "Texto 4", 
        max_length=80, 
        default="realizado na empresa fictícia na data", 
        blank=True, null=True
    )
    text_5 = models.CharField(
        "Texto 5", 
        max_length=400, 
        default="na Cidade de São Paulo. Estado de SP.", 
        blank=True, null=True
    )
    text_6 = models.CharField(
        "Texto 6", 
        max_length=80, 
        default="Com carga horária de:", 
        blank=True, null=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Modelo de Certificado"
        verbose_name_plural = "Modelos de Certificados"

    def __str__(self):
        return self.name
