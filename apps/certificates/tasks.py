"""
apps/certificates/tasks.py
Tarefas assíncronas Celery para emissão de certificados.
"""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def issue_certificate_task(self, registration_id: str):
    """
    Tarefa assíncrona: gera e envia o certificado.
    Acionada pelo painel quando o responsável clica em "Enviar Certificado".
    """
    from apps.certificates.services.certificate_service import issue_certificate

    logger.info("Iniciando emissão para inscrição %s", registration_id)
    result = issue_certificate(registration_id)

    if not result["success"]:
        logger.error("Falha na emissão: %s", result.get("error"))
        raise self.retry(exc=Exception(result.get("error", "Erro desconhecido")))

    logger.info(
        "Certificado emitido | e-mail=%s | whatsapp=%s",
        result["email_sent"],
        result["whatsapp_sent"],
    )
    return result
