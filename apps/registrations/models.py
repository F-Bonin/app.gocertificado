"""
apps/registrations/models.py
Modelo de solicitação de certificado do participante.
"""
import uuid
from django.db import models
from apps.core.models import Instructor, Course, RecurringEvent, EventSession


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
    profession = models.CharField("Função/Profissão", max_length=100, blank=True, null=True)
    birth_date = models.DateField("Data de nascimento", blank=True, null=True)
    email = models.EmailField("E-mail")
    whatsapp = models.CharField(
        "WhatsApp",
        max_length=20,
        blank=True, 
        null=True,
        help_text="Somente números com DDD. Ex.: 11999999999"
    )
    rg = models.CharField("RG", max_length=20, blank=True, null=True)
    cpf = models.CharField("CPF", max_length=14)

    # Endereço
    cep = models.CharField("CEP", max_length=9, blank=True, null=True)
    street = models.CharField("Rua", max_length=200, blank=True, null=True)
    number = models.CharField("Número", max_length=50, blank=True, null=True)
    complement = models.CharField("Complemento", max_length=100, blank=True, null=True)
    neighborhood = models.CharField("Bairro", max_length=100, blank=True, null=True)
    city = models.CharField("Cidade", max_length=100, blank=True, null=True)
    state = models.CharField("UF", max_length=2, blank=True, null=True)
    location_type = models.CharField(
        "Onde fica o endereço?", 
        max_length=20, 
        choices=[('condominio', '🏢 Condomínio (apartamento ou casa em condomínio)'), ('casa', '🏠 Casa (fora de condomínio)')], 
        default='casa'
    )
    condominium_name = models.CharField("Nome do Condomínio", max_length=200, blank=True, null=True)
    address_block = models.CharField("Bloco", max_length=50, blank=True, null=True)
    address_floor = models.CharField("Número/Letra do Andar", max_length=50, blank=True, null=True)
    address_apt = models.CharField("Número do Apartamento/Casa", max_length=50, blank=True, null=True)
    country = models.CharField("País", max_length=100, blank=True, null=True, default="Brasil")

    # Dados do Local
    institution_name = models.CharField("Nome do Local", max_length=200, null=True, blank=True)
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

    recurring_event = models.ForeignKey(
        'core.RecurringEvent', 
        on_delete=models.CASCADE, 
        related_name='registrations', 
        null=True, 
        blank=True, 
        verbose_name="Evento Recorrente"
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
    is_requested = models.BooleanField("Certificado Solicitado", default=False)
    checkin_at = models.DateTimeField("Data/Hora do Check-in", null=True, blank=True)
    certificate_requested = models.BooleanField("Certificado Solicitado", default=False)

    class Meta:
        verbose_name = "Solicitação de Certificado"
        verbose_name_plural = "Solicitações de Certificado"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.course_name}"

    @property
    def has_met_attendance(self) -> bool:
        """Verifica se o aluno atingiu a presença (100% Padrão ou % Mínima Recorrente)"""
        if self.course:
            return self.attended
        if self.recurring_event:
            event = self.recurring_event
            if event.event_type != 'SCHEDULED' or event.no_certificate:
                return False
            attended_hours = sum(p.session.hours for p in self.session_presences.filter(attended=True))
            required_hours = (event.hours * event.min_frequency) / 100.0
            return attended_hours >= required_hours
        return False

    @property
    def event_name_display(self):
        """Retorna o nome do evento associado (Course ou RecurringEvent) ou o legado."""
        if self.course:
            return self.course.name
        if self.recurring_event:
            return self.recurring_event.name
        return self.course_name

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


class NPSResponse(models.Model):
    """
    Armazena as respostas dos alunos para as pesquisas de satisfação vinculadas a uma inscrição específica.
    Essencial para coletar feedback quantitativo e qualitativo após a conclusão do evento,
    permitindo que as empresas analisem o NPS (Net Promoter Score) de seus treinamentos.
    """
    registration = models.ForeignKey(
        'Registration', 
        on_delete=models.CASCADE, 
        related_name='nps_responses', 
        verbose_name='Inscrição'
    )
    question = models.ForeignKey(
        'core.NPSQuestion', 
        on_delete=models.CASCADE, 
        related_name='responses', 
        verbose_name='Pergunta'
    )
    answer_score = models.IntegerField(null=True, blank=True, verbose_name='Nota')
    answer_text = models.TextField(null=True, blank=True, verbose_name='Resposta em Texto')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Resposta NPS"
        verbose_name_plural = "Respostas NPS"
        ordering = ['created_at']

    def __str__(self):
        return f"Resposta de {self.registration.full_name} para {self.question.text[:30]}"


class DynamicResponse(models.Model):
    """
    Armazena as respostas para campos de formulários dinâmicos.
    Arquitetura EAV: Este representa o Valor.
    Relaciona uma inscrição específica (Entidade) a um campo dinâmico (Atributo) e seu valor correspondente.
    """
    registration = models.ForeignKey(
        'Registration', 
        on_delete=models.CASCADE, 
        related_name='dynamic_responses',
        verbose_name="Inscrição"
    )
    field = models.ForeignKey(
        'core.DynamicField', 
        on_delete=models.CASCADE,
        verbose_name="Campo"
    )
    value = models.TextField("Valor", blank=True, null=True)

    class Meta:
        verbose_name = "Resposta Dinâmica"
        verbose_name_plural = "Respostas Dinâmicas"

    def __str__(self):
        return f"Resposta de {self.registration.full_name} para {self.field.label}"


class SessionPresence(models.Model):
    """Registro de presença de um participante em um encontro específico."""
    registration = models.ForeignKey(
        Registration, 
        on_delete=models.CASCADE, 
        related_name='session_presences',
        verbose_name="Inscrição"
    )
    session = models.ForeignKey(
        'core.EventSession', 
        on_delete=models.CASCADE, 
        related_name='presences',
        verbose_name="Encontro"
    )
    attended = models.BooleanField("Presente", default=False)
    checkin_at = models.DateTimeField("Data/Hora do Check-in", null=True, blank=True)

    class Meta:
        verbose_name = "Presença no Encontro"
        verbose_name_plural = "Presenças nos Encontros"
        unique_together = ('registration', 'session')

    def __str__(self):
        return f"{self.registration.full_name} — {self.session.theme}"
