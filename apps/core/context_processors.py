from django.conf import settings

def company_info(request):
    """
    Disponibiliza informações da empresa em todos os templates.
    """
    return {
        'COMPANY_NAME': settings.COMPANY_NAME,
        'COMPANY_LOGO_URL': settings.COMPANY_LOGO_URL,
    }
