"""
config/urls.py — Roteamento principal
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),

    # Redirecionamento da raiz para o Dashboard
    path("", RedirectView.as_view(pattern_name="certificates:dashboard", permanent=False), name="home"),

    # Formulário de inscrição (acesso público)
    path("", include("apps.registrations.urls", namespace="registrations")),

    # Autenticação SaaS
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),

    # Gestão de certificados (acesso restrito ao responsável)
    path("painel/", include("apps.certificates.urls", namespace="certificates")),

    # Configurações da Empresa e Instrutores (SaaS)
    path("painel/configuracoes/", include("apps.core.urls", namespace="core")),
]

# Debug toolbar (somente em desenvolvimento)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
