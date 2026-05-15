from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'is_company_admin', 'must_change_password')
    list_filter = ('is_company_admin', 'company')
    search_fields = ('user__username', 'user__email', 'company__name')
    
    fieldsets = (
        ('Identificação da Conta', {
            'fields': ('user', 'company', 'is_company_admin', 'must_change_password')
        }),
        ('Permissões do Módulo (GoCertificado)', {
            'description': 'Atenção: Desmarcar as opções ocultará o menu e bloqueará o acesso na URL.',
            'fields': (
                'perm_dashboard', 'perm_company', 'perm_cert_design',
                'perm_instructors', 'perm_nps', 'perm_custom_forms',
                'perm_standard_events', 'perm_recurring_events',
                'perm_my_events', 'perm_participants', 'perm_certificates_panel'
            )
        }),
    )
