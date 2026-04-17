"""
apps/core/models.py
Modelos base: Empresa e Instrutor.
"""
import uuid
from django.db import models
from django.utils.text import slugify


class Company(models.Model):
    """Empresa ou organização que emite os certificados."""
    name = models.CharField(
        "Nome da empresa", 
        max_length=200,
        help_text="Atenção: A informação deste campo sairá impressa no certificado do aluno."
    )
    logo = models.ImageField(
        upload_to='company_logos/', 
        blank=True, 
        null=True,
        help_text="Atenção: A informação deste campo sairá impressa no certificado do aluno."
    )
    cnpj = models.CharField(
        "CNPJ ou CPF",
        max_length=20, 
        blank=True, 
        null=True,
        help_text="Atenção! Seu CNPJ sairá no certificado do seu aluno. Se for emitir como pessoa física, preencha com CPF."
    )
    website = models.URLField(
        "Site", 
        blank=True,
        help_text="Atenção: A informação deste campo sairá impressa no certificado do aluno."
    )
    email = models.EmailField(
        "E-mail", 
        help_text="Atenção: Este e-mail receberá as respostas dos alunos."
    )
    logo_position = models.CharField(
        "Posição da Logo", 
        max_length=20, 
        choices=[
            ('none', '1. Não adicionar Logo'), 
            ('center', '2. Logo no centro e topo'), 
            ('left', '3. Logo à esquerda e topo'), 
            ('right', '4. Logo à direita e topo')
        ], 
        default='center'
    )
    certificate_model = models.CharField(
        "Modelo de Certificado Ativo", 
        max_length=20, 
        choices=[
            ('default', 'Modelo Padrão (Do sistema)'), 
            ('custom', 'Modelo Personalizado')
        ], 
        blank=True, 
        null=True
    )
    custom_template = models.ImageField("Modelo de Certificado Personalizado (A4 Paisagem)", upload_to='company/templates/', blank=True, null=True)
    custom_title = models.CharField("Título do Certificado", max_length=80, default="Certificado de Conclusão", blank=True, null=True)
    custom_text_1 = models.CharField("Texto 1", max_length=80, default="Certificamos que", blank=True, null=True)
    custom_text_2 = models.CharField("Texto 2", max_length=80, default="portador do CPF", blank=True, null=True)
    custom_text_3 = models.CharField("Texto 3", max_length=80, default="concluiu com êxito o curso/treinamento", blank=True, null=True)
    custom_text_4 = models.CharField("Texto 4", max_length=80, default="realizado na empresa fictícia na data", blank=True, null=True)
    custom_text_5 = models.CharField("Texto 5", max_length=400, default="na Cidade de São Paulo. Estado de SP.", blank=True, null=True)
    custom_text_6 = models.CharField("Texto 6", max_length=80, default="Com carga horária de:", blank=True, null=True)
    active = models.BooleanField("Ativo", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self):
        return self.name


class NPSForm(models.Model):
    """
    Modelo que representa o formulário de pesquisa de satisfação (NPS).
    Utilizado para isolamento multitenant, permitindo que cada empresa tenha seus próprios formulários personalizados.
    """
    company = models.ForeignKey(
        'Company', 
        on_delete=models.CASCADE, 
        related_name='nps_forms', 
        verbose_name='Empresa'
    )
    name = models.CharField(max_length=200, verbose_name='Nome do Formulário')
    is_mandatory = models.BooleanField(default=False, verbose_name='Resposta Obrigatória?')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Formulário NPS"
        verbose_name_plural = "Formulários NPS"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class NPSQuestion(models.Model):
    """
    Representa as perguntas individuais de um formulário NPS.
    Permite coletar feedbacks quantitativos (notas) e qualitativos (texto livre) dos alunos.
    """
    nps_form = models.ForeignKey(
        NPSForm, 
        on_delete=models.CASCADE, 
        related_name='questions', 
        verbose_name='Formulário'
    )
    text = models.CharField(max_length=500, verbose_name='Pergunta')
    question_type = models.CharField(
        max_length=10, 
        choices=[('score', 'Nota (0 a 10)'), ('text', 'Texto Livre')], 
        default='score', 
        verbose_name='Tipo de Pergunta'
    )
    order = models.PositiveIntegerField(default=0, verbose_name='Ordem')

    class Meta:
        verbose_name = "Pergunta NPS"
        verbose_name_plural = "Perguntas NPS"
        ordering = ['order']

    def __str__(self):
        return self.text


class DynamicForm(models.Model):
    """
    Representa um formulário dinâmico que pode ser associado a cursos.
    Arquitetura EAV (Entity-Attribute-Value): Este é o contêiner (Entidade).
    Permite que cada empresa crie formulários personalizados para inscrição ou solicitação de certificado.
    """
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='dynamic_forms', 
        verbose_name="Empresa"
    )
    name = models.CharField("Nome do Formulário", max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Formulário Dinâmico"
        verbose_name_plural = "Formulários Dinâmicos"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class DynamicField(models.Model):
    """
    Representa um campo individual dentro de um formulário dinâmico.
    Arquitetura EAV: Este representa o Atributo.
    Define o tipo de dado, rótulo e obrigatoriedade de cada campo do formulário.
    """
    FIELD_TYPES = [
        ('text', 'Texto Curto'),
        ('email', 'E-mail'),
        ('number', 'Número'),
        ('date', 'Data'),
        ('select', 'Seleção (Dropdown)'),
        ('checkbox', 'Caixa de Seleção'),
    ]
    form = models.ForeignKey(
        DynamicForm, 
        on_delete=models.CASCADE, 
        related_name='fields', 
        verbose_name="Formulário"
    )
    label = models.CharField("Rótulo do Campo", max_length=200)
    field_type = models.CharField("Tipo do Campo", max_length=20, choices=FIELD_TYPES)
    is_required = models.BooleanField("Obrigatório?", default=False)
    options = models.CharField(
        "Opções", 
        max_length=500, 
        blank=True, 
        null=True, 
        help_text="Valores separados por vírgula para campos select"
    )
    order = models.PositiveIntegerField("Ordem", default=0)

    class Meta:
        verbose_name = "Campo Dinâmico"
        verbose_name_plural = "Campos Dinâmicos"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.label} ({self.get_field_type_display()})"


class Instructor(models.Model):
    """Instrutor que ministra treinamentos."""
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="instructors",
        verbose_name="Empresa"
    )
    full_name = models.CharField("Nome completo", max_length=200)
    role = models.CharField("Função/Cargo", max_length=100, blank=True, null=True)
    credentials = models.CharField(
        "Credenciais / Título",
        max_length=300,
        help_text="Ex.: Engenheiro de Segurança do Trabalho — CREA 123456"
    )
    signature_image = models.ImageField(
        "Imagem da Assinatura",
        upload_to='signatures/',
        blank=True, null=True
    )
    signature = models.ImageField(
        "Assinatura (Antiga)",
        upload_to="instructors/signatures/",
        blank=True, null=True
    )
    email = models.EmailField("E-mail", blank=True)
    active = models.BooleanField("Ativo", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Assinatura do Certificado"
        verbose_name_plural = "Assinaturas do Certificado"
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name} — {self.role or self.credentials}"


class Course(models.Model):
    """Modelo persistente de Treinamentos."""
    name = models.CharField("Nome do curso", max_length=300)
    slug = models.SlugField("Slug", max_length=350, unique=True, blank=True, null=True)
    start_date = models.DateField("Data de Início")
    end_date = models.DateField("Data de Término", null=True, blank=True)
    city = models.CharField("Cidade", max_length=100)
    state = models.CharField("Estado (UF)", max_length=2)
    hours = models.PositiveIntegerField("Carga horária (horas)")
    
    # Dados da Instituição
    cep = models.CharField('CEP', max_length=9, blank=True, null=True)
    institution_name = models.CharField("Nome da Instituição", max_length=200, null=True, blank=True)
    institution_street = models.CharField("Rua/Avenida", max_length=200, null=True, blank=True)
    institution_number = models.CharField("Número", max_length=50, null=True, blank=True)
    institution_neighborhood = models.CharField("Bairro", max_length=100, null=True, blank=True)
    institution_complement = models.CharField("Complemento", max_length=100, null=True, blank=True)
    
    signature_1 = models.ForeignKey(
        Instructor, 
        related_name='course_sig1', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Assinatura 1"
    )
    signature_2 = models.ForeignKey(
        Instructor, 
        related_name='course_sig2', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Assinatura 2"
    )
    signature_3 = models.ForeignKey(
        Instructor, 
        related_name='course_sig3', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Assinatura 3"
    )
    
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name="courses",
        verbose_name="Empresa"
    )
    
    certificate_template = models.ForeignKey(
        'certificates.CertificateTemplate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Modelo de Certificado",
        help_text='Selecione o layout personalizado para os certificados deste treinamento'
    )
    nps_form = models.ForeignKey('core.NPSForm', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Formulário NPS", help_text="Selecione a pesquisa de satisfação para este evento")
    
    custom_reg_form = models.ForeignKey(
        'DynamicForm', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='reg_courses', 
        verbose_name='Formulário de Inscrição Personalizado'
    )
    custom_cert_form = models.ForeignKey(
        'DynamicForm', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='cert_courses', 
        verbose_name='Formulário de Solicitação Personalizado'
    )

    link_hash = models.UUIDField(
        "Link Único", 
        default=None, 
        null=True, 
        blank=True, 
        unique=True
    )
    checkin_hash = models.UUIDField("Hash de Credenciamento", null=True, blank=True, unique=True)
    registration_start = models.DateTimeField("Início das Inscrições", blank=True, null=True)
    registration_end = models.DateTimeField("Término das Inscrições", blank=True, null=True)
    expires_at = models.DateTimeField("Expiração do Certificado", blank=True, null=True)
    no_certificate = models.BooleanField("Este evento não terá certificado", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Treinamento"
        verbose_name_plural = "Treinamentos"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.name} — {self.city} ({self.start_date})"

    def save(self, *args, **kwargs):
        """Gera um slug amigável único e um hash de credenciamento se estiverem vazios."""
        if not self.slug:
            # Concatena o nome slugificado com os 4 primeiros dígitos de um UUID para unicidade absoluta
            self.slug = f"{slugify(self.name)}-{str(uuid.uuid4())[:4]}"
        
        if not self.checkin_hash:
            self.checkin_hash = uuid.uuid4()
            
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Verifica se a solicitação de certificado já expirou baseado na data atual."""
        from django.utils import timezone
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    def get_registration_url(self):
        """Retorna a URL limpa de inscrição utilizando o novo padrão de Slug."""
        from django.urls import reverse
        if not self.slug:
            return ""
        # Sênior Fix: Apontando obrigatoriamente para o formulário de Inscrição (Pré-evento)
        return reverse("registrations:event_form", kwargs={"slug": self.slug})
