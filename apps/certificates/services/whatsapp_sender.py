import logging
import httpx
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)
WAHA_TIMEOUT = 30  # segundos


def _headers() -> dict:
    headers = {"Content-Type": "application/json"}
    if settings.WAHA_API_KEY:
        headers["X-Api-Key"] = settings.WAHA_API_KEY
    return headers


def _base_url() -> str:
    return settings.WAHA_BASE_URL.rstrip("/")


def check_waha_session() -> bool:
    """Verifica se a sessão WAHA está ativa."""
    try:
        resp = httpx.get(
            f"{_base_url()}/api/sessions/{settings.WAHA_SESSION}",
            headers=_headers(),
            timeout=10,
        )
        data = resp.json()
        return data.get("status") in ("WORKING", "CONNECTED")
    except Exception as exc:
        logger.error("Erro ao verificar sessão WAHA: %s", exc)
        return False


def send_certificate_whatsapp(certificate) -> bool:
    """
    Envia mensagem de texto com link do PDF para o WhatsApp do participante.
    Retorna True se enviado com sucesso.
    """
    if not getattr(settings, "WAHA_ENABLED", False):
        return True  # Silenciosamente ignoramos o envio se desabilitado

    reg = certificate.registration
    if not certificate.pdf_file:
        logger.error("Certificado %s sem PDF.", certificate.numeric_code)
        return False

    chat_id = reg.whatsapp_formatted

    # Monta a URL pública do PDF
    pdf_url = f"{settings.WAHA_DJANGO_BASE_URL.rstrip('/')}{certificate.pdf_file.url}"

    # Prepara os dados para o payload
    first_name = reg.full_name.split()[0] if reg.full_name else "Participante"
    
    # Mensagem de texto com link para download do PDF
    mensagem = (
        f"🎓 Parabéns, {first_name}!\n\n"
        f"Seu certificado do treinamento *{reg.course.name}* está pronto.\n\n"
        f"📄 Baixe seu certificado em PDF:\n"
        f"{pdf_url}\n\n"
        f"🔍 Para verificar a autenticidade, acesse:\n"
        f"{certificate.verification_url}\n\n"
        f"🔑 Código de verificação: {certificate.numeric_code_formatted}\n\n"
        f"_{settings.COMPANY_NAME}_"
    )

    # Payload exatamente com as 3 chaves obrigatórias exigidas pelo WAHA
    payload = {
        "chatId": chat_id,
        "text": mensagem,
        "session": settings.WAHA_SESSION,
    }

    try:
        resp = httpx.post(
            f"{_base_url()}/api/sendText",
            json=payload,
            headers=_headers(),
            timeout=WAHA_TIMEOUT,
        )
        resp.raise_for_status()

        certificate.whatsapp_sent = True
        certificate.whatsapp_sent_at = timezone.now()
        certificate.save(update_fields=["whatsapp_sent", "whatsapp_sent_at"])
        logger.info("Mensagem enviada via WhatsApp para %s", chat_id)
        return True

    except Exception as exc:
        logger.error("Falha ao enviar WhatsApp para %s: %s", chat_id, exc)
        return False