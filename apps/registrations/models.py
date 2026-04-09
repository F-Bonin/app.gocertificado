"""
apps/registrations/models.py
Modelo de solicitação de certificado do participante.
"""
import uuid
from django.db import models
from apps.core.models import Instructor, Course


class Registration(models.Model):
    """Solicitação de certificado de um participante em um treinamento."""

    class Status(models.TextChoices):
        PENDING = "pending", "Aguardando envio"
        SENT = "sent", "Certificado enviado"

    # Identificação
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField("Cadastrado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)
    status = models.CharField(
        "Status", max_length=10, choices=Status.choices, default=Status.PENDING
    )

    # Dados pessoais
    full_name = models.CharField("Nome completo", max_length=200)
    gender = models.CharField(
        "Gênero", 
        max_length=1, 
        choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')], 
        blank=True, 
        null=True
    )
    custom_gender = models.CharField("Qual?", max_length=50, blank=True, null=True)
    profession = models.CharField("Profissão", max_length=100, blank=True, null=True)
    birth_date = models.DateField("Data de nascimento")
    email = models.EmailField("E-mail")
    whatsapp = models.CharField(
        "WhatsApp",
        max_length=20,
        help_text="Somente números com DDD. Ex.: 11999999999"
    )
    rg = models.CharField("RG", max_length=20)
    cpf = models.CharField("CPF", max_length=14)

    # Endereço
    cep = models.CharField("CEP", max_length=9, blank=True, null=True)
    street = models.CharField("Rua", max_length=200, blank=True, null=True)
    number = models.CharField("Número", max_length=50, blank=True, null=True)
    complement = models.CharField("Complemento", max_length=100, blank=True, null=True)
    neighborhood = models.CharField("Bairro", max_length=100, blank=True, null=True)
    city = models.CharField("Cidade", max_length=100, blank=True, null=True)
    state = models.CharField("UF", max_length=2, blank=True, null=True)

    # Dados da Instituição
    institution_name = models.CharField("Nome da Instituição", max_length=200, null=True, blank=True)
    institution_street = models.CharField("Rua/Avenida", max_length=200, null=True, blank=True)
    institution_number = models.CharField("Número", max_length=50, null=True, blank=True)
    institution_neighborhood = models.CharField("Bairro", max_length=100, null=True, blank=True)
    institution_complement = models.CharField("Complemento", max_length=100, null=True, blank=True)

    # Dados do treinamento (Campos Legados - Manter Null para não quebrar novas inscrições)
    course_name = models.CharField("Nome do curso/treinamento", max_length=300, null=True, blank=True)
    course_date = models.DateField(null=True, blank=True)
    course_workload = models.PositiveIntegerField("Carga horária (horas)", null=True, blank=True)

    # Vínculo com treinamento persistente
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        related_name='registrations', 
        null=True, 
        blank=True,
        verbose_name="Treinamento"
    )

    # Vínculo com instrutor (definido pelo responsável via painel)
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="registrations",
        verbose_name="Instrutor"
    )

    attended = models.BooleanField("Presença Confirmada", default=False)

    class Meta:
        verbose_name = "Solicitação de Certificado"
        verbose_name_plural = "Solicitações de Certificado"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.course_name}"

    @property
    def whatsapp_formatted(self) -> str:
        """Retorna número no formato esperado pelo WAHA: 5511999999999@c.us"""
        digits = "".join(filter(str.isdigit, self.whatsapp))
        if not digits.startswith("55"):
            digits = "55" + digits
        return f"{digits}@c.us"

    @property
    def cpf_masked(self) -> str:
        """CPF com dígitos centrais ocultos para exibição pública (Ex: 123.***.***-01)."""
        digits = "".join(filter(str.isdigit, self.cpf))
        if len(digits) == 11:
            return f"{digits[:3]}.***.***-{digits[9:]}"
        # Se não tiver 11 dígitos mas for possível mascarar parcialmente
        if len(digits) > 4:
            return f"{digits[:3]}...{digits[-2:]}"
        return self.cpf
