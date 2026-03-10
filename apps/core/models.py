"""
apps/core/models.py
Modelos base: Empresa e Instrutor.
"""
import uuid
from django.db import models


class Company(models.Model):
    """Empresa ou organização que emite os certificados."""
    name = models.CharField("Nome da empresa", max_length=200)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    cnpj = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField("Site", blank=True)
    active = models.BooleanField("Ativo", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self):
        return self.name


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
    start_date = models.DateField("Data de Início", null=True, blank=True)
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
    
    link_hash = models.UUIDField(
        "Link Único", 
        default=None, 
        null=True, 
        blank=True, 
        unique=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Treinamento"
        verbose_name_plural = "Treinamentos"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.name} — {self.city} ({self.start_date})"

    def get_registration_url(self):
        """Constrói a URL de inscrição com todos os dados via QueryString."""
        from django.urls import reverse
        from urllib.parse import urlencode
        
        if not self.link_hash:
            return ""
            
        base_url = reverse("registrations:form", kwargs={"link_hash": self.link_hash})
        
        params = {
            "course_name": self.name,
            "course_date": self.start_date.isoformat() if self.start_date else "",
            "course_city": self.city,
            "course_state": self.state,
            "course_workload": self.hours,
            "institution_name": self.institution_name or "",
            "institution_street": self.institution_street or "",
            "institution_number": self.institution_number or "",
            "institution_neighborhood": self.institution_neighborhood or "",
            "institution_complement": self.institution_complement or "",
        }
        
        return f"{base_url}?{urlencode(params)}"
