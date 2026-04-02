"""
apps/certificates/services/pdf_generator.py
Gera o certificado em PDF usando ReportLab com layout profissional e identidade SaaS.
"""
import io
import qrcode
from PIL import Image
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white, black, transparent
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from django.conf import settings
from pathlib import Path

# Cores e Estilos
COLOR_PRIMARY = HexColor("#1a3a5c")    # Azul escuro
COLOR_SECONDARY = HexColor("#c8a45a")  # Dourado
COLOR_TEXT = HexColor("#2d2d2d")


def _qr_image(url: str) -> Image.Image:
    """Gera imagem PIL do QR Code."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")


def _pil_to_reader(img: Image.Image) -> ImageReader:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)


def generate_certificate_pdf(certificate) -> bytes:
    """
    Recebe um objeto Certificate e retorna os bytes do PDF gerado.
    Utiliza ReportLab para desenhar o layout conforme solicitado.
    """
    reg = certificate.registration
    course = reg.course
    
    company = course.company if course else None

    buf = io.BytesIO()
    w, h = landscape(A4)
    c = canvas.Canvas(buf, pagesize=landscape(A4))

    # ── Fundo (Totalmente Branco) ──────────────────────────────────
    c.setFillColor(white)
    c.rect(0, 0, w, h, fill=1, stroke=0)

    # ── Bordas Decorativas ─────────────────────────────────────────
    # Borda externa dourada
    c.setStrokeColor(COLOR_SECONDARY)
    c.setLineWidth(4)
    c.rect(0.8 * cm, 0.8 * cm, w - 1.6 * cm, h - 1.6 * cm, fill=0, stroke=1)

    # ── Logo da Empresa (Topo e Centro) ────────────────────────────
    logo_reader = None
    if company and company.logo:
        logo_path = Path(settings.MEDIA_ROOT) / str(company.logo)
        if logo_path.exists():
            try:
                logo_img = Image.open(logo_path)
                logo_reader = _pil_to_reader(logo_img)
            except Exception:
                pass
    
    if logo_reader:
        # Logo grande e em destaque
        logo_w, logo_h = 8 * cm, 4 * cm
        c.drawImage(
            logo_reader,
            (w - logo_w) / 2, h - 5.5 * cm,
            width=logo_w, height=logo_h,
            preserveAspectRatio=True, mask="auto"
        )

    # ── Título Centralizado ────────────────────────────────────────
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(w / 2, h - 7.5 * cm, "CERTIFICADO DE CONCLUSÃO")

    # ── Lógica de Datas ───────────────────────────────────────────
    if course and course.start_date:
        start_d = course.start_date
        end_d = course.end_date
        if end_d and end_d != start_d:
            date_string = f"de {start_d.strftime('%d/%m/%Y')} a {end_d.strftime('%d/%m/%Y')}"
        else:
            date_string = f"{start_d.strftime('%d/%m/%Y')}"
    else:
        # Fallback para dados da inscrição (legado ou manual)
        date_string = reg.course_date.strftime('%d/%m/%Y') if reg.course_date else ""

    # ── Corpo do Texto (Formatado em Linhas) ──────────────────────
    full_name = reg.full_name.upper()
    course_name_text = (course.name.upper() if course and course.name else reg.course_name.upper()) if (course and course.name or reg.course_name) else ""
    institution_name = (course.institution_name if course and course.institution_name else reg.institution_name) or ""
    city = (course.city.upper() if course and course.city else (reg.city.upper() if reg.city else ""))
    state = (course.state.upper() if course and course.state else (reg.state.upper() if reg.state else ""))
    workload = course.hours if course else reg.course_workload
    workload_str = f"{workload}h" if workload is not None else ""
    
    # Linha 1: Certificamos que
    c.setFont("Helvetica", 14)
    c.setFillColor(COLOR_TEXT)
    current_y = h - 8.23 * cm
    c.drawCentredString(w / 2, current_y, "Certificamos que")
    
    # Linha 2: Nome do Participante (Destaque)
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(COLOR_PRIMARY)
    current_y -= 1.0 * cm
    c.drawCentredString(w / 2, current_y, full_name)
    
    # Linha 3: portador do CPF...
    c.setFont("Helvetica", 14)
    c.setFillColor(COLOR_TEXT)
    current_y -= 0.9 * cm
    c.drawCentredString(w / 2, current_y, f"portador do CPF {reg.cpf} concluiu com êxito o curso/treinamento")
    
    # Linha 4: Nome do Curso (Destaque)
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(COLOR_PRIMARY)
    current_y -= 1.1 * cm
    c.drawCentredString(w / 2, current_y, course_name_text)
    
    # Linha 5: Local...
    c.setFont("Helvetica", 12)
    c.setFillColor(COLOR_TEXT)
    current_y -= 0.9 * cm
    local_text = f"Local: {institution_name} realizado em {date_string} - {city}/{state}."
    c.drawCentredString(w / 2, current_y, local_text)
    
    # Linha 6: Carga Horária...
    c.setFont("Helvetica", 14)
    c.setFillColor(black)
    current_y -= 0.7 * cm
    c.drawCentredString(w / 2, current_y, f"Carga Horária: {workload_str}.")

    # ── Assinaturas (Rodapé Dinâmico) ─────────────────────────────
    signatures = []
    # As assinaturas são obtidas do curso vinculado
    if course:
        if course.signature_1: signatures.append(course.signature_1)
        if course.signature_2: signatures.append(course.signature_2)
        if course.signature_3: signatures.append(course.signature_3)

    if signatures:
        num_sig = len(signatures)
        footer_y = 5 * cm
        sig_width = 6 * cm
        gap = 1.5 * cm
        total_width = (num_sig * sig_width) + ((num_sig - 1) * gap)
        start_x = (w - total_width) / 2

        for i, sig in enumerate(signatures):
            current_x = start_x + (i * (sig_width + gap))
            sig_file = sig.signature_image or sig.signature
            if sig_file:
                sig_path = Path(settings.MEDIA_ROOT) / str(sig_file)
                if sig_path.exists():
                    try:
                        sig_img = Image.open(sig_path)
                        sig_reader = _pil_to_reader(sig_img)
                        c.drawImage(
                            sig_reader,
                            current_x, footer_y - 0.7 * cm,
                            width=sig_width, height=2 * cm,
                            preserveAspectRatio=True, mask="auto"
                        )
                    except Exception:
                        pass

            c.setStrokeColor(black)
            c.setLineWidth(0.5)
            c.line(current_x, footer_y - 0.2 * cm, current_x + sig_width, footer_y - 0.2 * cm)
            
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(current_x + (sig_width / 2), footer_y - 0.6 * cm, sig.full_name)
            
            c.setFont("Helvetica", 9)
            role_text = sig.role or sig.credentials
            c.drawCentredString(current_x + (sig_width / 2), footer_y - 1.0 * cm, role_text)

    # Rodapé Integrado (QR Code + Dados da Empresa) ──────────────
    qr_size = 2.5 * cm  # Reduzido de 3.0cm (~15%)
    qr_y = 1.1 * cm     # Posição Y comum para o bloco do rodapé

    # Prepara os textos
    if company:
        # Lógica para definir se é CNPJ ou CPF
        raw_cnpj = "".join(filter(str.isdigit, company.cnpj or ""))
        doc_label = "CPF" if len(raw_cnpj) <= 11 else "CNPJ"
        company_text = f"{company.name} - {doc_label}: {company.cnpj or 'N/A'}"
    else:
        company_text = ""

    code_text = f"Código: {certificate.numeric_code_formatted}"
    url_text = certificate.verification_url
    
    # Calcula larguras para centralização total do bloco
    gap = 0.6 * cm
    # Consideramos a maior largura entre os textos para o cálculo do bloco
    max_text_w = max(
        c.stringWidth(company_text, "Helvetica", 10) if company else 0,
        c.stringWidth(code_text, "Helvetica-Bold", 8),
        c.stringWidth(url_text, "Helvetica", 7)
    )
    total_block_width = qr_size + gap + max_text_w
    block_start_x = (w - total_block_width) / 2

    # 1. Desenha QR Code
    qr_img = _qr_image(certificate.verification_url)
    qr_reader = _pil_to_reader(qr_img)
    c.drawImage(qr_reader, block_start_x, qr_y, width=qr_size, height=qr_size)

    # 2. Desenha Bloco de Texto à direita do QR Code
    text_x = block_start_x + qr_size + gap
    
    # Empresa e CNPJ
    if company:
        c.setFont("Helvetica", 10)
        c.setFillColor(COLOR_TEXT)
        c.drawString(text_x, qr_y + 1.6 * cm, company_text)

    # Código de Verificação
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(black)
    c.drawString(text_x, qr_y + 1.0 * cm, code_text)

    # URL de Verificação
    c.setFont("Helvetica", 7)
    c.drawString(text_x, qr_y + 0.5 * cm, url_text)

    c.save()
    return buf.getvalue()
