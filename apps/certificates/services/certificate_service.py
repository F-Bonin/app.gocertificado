"""
apps/certificates/services/certificate_service.py
Orquestra: geração do PDF → salvar → enviar por e-mail e WhatsApp.
"""
import logging
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils import timezone

from apps.registrations.models import Registration
from apps.certificates.models import Certificate
from .pdf_generator import generate_certificate_pdf
from .email_sender import send_certificate_email
from .whatsapp_sender import send_certificate_whatsapp

logger = logging.getLogger(__name__)


def issue_certificate(registration_id: str) -> dict:
    """
    Fluxo completo de emissão de certificado:
      1. Obtém (ou cria) o objeto Certificate
      2. Gera o PDF
      3. Salva o PDF no banco/storage
      4. Envia por e-mail
      5. Envia por WhatsApp
      6. Atualiza o status da inscrição

    Retorna dicionário com resultados de cada etapa.
    """
    result = {
        "success": False,
        "pdf_generated": False,
        "email_sent": False,
        "whatsapp_sent": False,
        "error": None,
    }

    try:
        reg = Registration.objects.select_related("course").get(pk=registration_id)
    except Registration.DoesNotExist:
        result["error"] = f"Inscrição {registration_id} não encontrada."
        logger.error(result["error"])
        return result

    # Cria ou recupera o certificado
    certificate, created = Certificate.objects.get_or_create(registration=reg)

    # ── 1. Gera PDF ───────────────────────────────────────────────
    try:
        pdf_bytes = generate_certificate_pdf(certificate)
        filename = (
            f"cert_{certificate.numeric_code}_"
            f"{reg.full_name.replace(' ', '_').lower()}.pdf"
        )
        certificate.pdf_file.save(filename, ContentFile(pdf_bytes), save=True)
        result["pdf_generated"] = True
        logger.info("PDF gerado: %s", filename)
    except Exception as exc:
        result["error"] = f"Erro na geração do PDF: {exc}"
        logger.error(result["error"])
        return result

    # ── 2. Envia e-mail ───────────────────────────────────────────
    result["email_sent"] = send_certificate_email(certificate)

    # ── 3. Envia WhatsApp ─────────────────────────────────────────
    result["whatsapp_sent"] = send_certificate_whatsapp(certificate)

    # ── 4. Atualiza status da inscrição ───────────────────────────
    reg.status = Registration.Status.SENT
    reg.save(update_fields=["status", "updated_at"])

    result["success"] = result["pdf_generated"]
    return result
