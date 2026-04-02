"""
apps/certificates/services/email_sender.py
Envia o certificado em PDF por e-mail.
"""
import logging
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def send_certificate_email(certificate) -> bool:
    """
    Envia o PDF do certificado para o e-mail do participante.
    Retorna True se enviado com sucesso.
    """
    reg = certificate.registration

    if not certificate.pdf_file:
        logger.error("Certificado %s não tem PDF gerado.", certificate.numeric_code)
        return False

    try:
        subject = f"Seu Certificado — {reg.course.name}"
        body = render_to_string(
            "emails/certificate_email.html",
            {
                "participant_name": reg.full_name.split()[0],
                "full_name": reg.full_name,
                "course_name": reg.course.name,
                "company_name": settings.COMPANY_NAME,
                "verification_url": certificate.verification_url,
                "numeric_code": certificate.numeric_code_formatted,
            }
        )

        # Extrai o e-mail da empresa vinculada ao curso da inscrição.
        # Usa DEFAULT_FROM_EMAIL como fallback de segurança.
        company_email = settings.DEFAULT_FROM_EMAIL
        if reg.course and hasattr(reg.course, 'company') and reg.course.company and reg.course.company.email:
            company_email = reg.course.company.email

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[reg.email],
            reply_to=[company_email],
        )
        email.content_subtype = "html"

        # Anexa o PDF
        certificate.pdf_file.open("rb")
        pdf_bytes = certificate.pdf_file.read()
        certificate.pdf_file.close()

        filename = f"certificado_{reg.full_name.replace(' ', '_').lower()}.pdf"
        email.attach(filename, pdf_bytes, "application/pdf")
        email.send(fail_silently=False)

        # Registra envio
        certificate.email_sent = True
        certificate.email_sent_at = timezone.now()
        certificate.save(update_fields=["email_sent", "email_sent_at"])

        logger.info("E-mail enviado para %s (%s)", reg.email, reg.full_name)
        return True

    except Exception as exc:
        logger.error("Falha ao enviar e-mail para %s: %s", reg.email, exc)
        return False
