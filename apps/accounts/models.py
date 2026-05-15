from django.db import models
from django.contrib.auth.models import User
from apps.core.models import Company


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='users')
    
    # Controle de Conta
    is_company_admin = models.BooleanField("É Administrador da Empresa?", default=False)
    must_change_password = models.BooleanField("Deve alterar a senha?", default=False)

    # Permissões Granulares de Módulos (Padrão: Acesso Total)
    perm_dashboard = models.BooleanField("Acesso ao Dashboard", default=True)
    perm_company = models.BooleanField("Acesso a Minha Organização", default=True)
    perm_cert_design = models.BooleanField("Acesso a Configurar Certificado", default=True)
    perm_instructors = models.BooleanField("Acesso a Assinatura Certificado", default=True)
    perm_nps = models.BooleanField("Acesso a Form NPS", default=True)
    perm_custom_forms = models.BooleanField("Acesso a Form Personalizado", default=True)
    perm_standard_events = models.BooleanField("Acesso a Criar Evento Padrão", default=True)
    perm_recurring_events = models.BooleanField("Acesso a Criar Evento Recorrente", default=True)
    perm_my_events = models.BooleanField("Acesso a Meus Eventos", default=True)
    perm_participants = models.BooleanField("Acesso a Alunos/Participantes", default=True)
    perm_certificates_panel = models.BooleanField("Acesso a Central de Certificados", default=True)

    def __str__(self):
        role = "[ADMIN]" if self.is_company_admin else "[MEMBRO]"
        return f"{self.user.username} {role} - {self.company.name}"
