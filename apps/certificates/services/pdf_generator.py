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
    empresa = reg.instructor.company if (reg.instructor and reg.instructor.company) else (course.company if (course and course.company) else None)

    buf = io.BytesIO()
    w, h = landscape(A4)
    c = canvas.Canvas(buf, pagesize=landscape(A4))

    # ── Cores Locais (Podem ser alteradas conforme o modelo) ────────
    primary_color = COLOR_PRIMARY
    secondary_color = COLOR_SECONDARY

    # ── Lógica de Fundo ───────────────────────────────────────────
    is_custom = empresa and empresa.certificate_model == 'custom' and empresa.custom_template
    
    if is_custom:
        # Desenha template personalizado cobrindo toda a folha
        template_path = Path(settings.MEDIA_ROOT) / str(empresa.custom_template)
        if template_path.exists():
            try:
                c.drawImage(str(template_path), 0, 0, width=w, height=h)
            except Exception:
                # Fallback se a imagem der erro
                c.setFillColor(white)
                c.rect(0, 0, w, h, fill=1, stroke=0)
    else:
        # Modelo Padrão (Default)
        primary_color = HexColor("#404040")
        secondary_color = HexColor("#A0A0A0")

        # Fundo Branco
        c.setFillColor(white)
        c.rect(0, 0, w, h, fill=1, stroke=0)

        # Bordas Decorativas (Borda externa dourada/secundária)
        c.setStrokeColor(secondary_color)
        c.setLineWidth(4)
        c.rect(0.8 * cm, 0.8 * cm, w - 1.6 * cm, h - 1.6 * cm, fill=0, stroke=1)

    # ── Lógica da Logo (Alinhamento Dinâmico) ─────────────────────
    logo_reader = None
    if empresa and empresa.logo and empresa.logo_position != 'none':
        logo_path = Path(settings.MEDIA_ROOT) / str(empresa.logo)
        if logo_path.exists():
            try:
                logo_img = Image.open(logo_path)
                logo_reader = _pil_to_reader(logo_img)
            except Exception:
                pass
    
    if logo_reader:
        logo_w = 4 * cm
        logo_h = 2 * cm # Altura proporcional máxima estimada
        pos = empresa.logo_position
        
        if pos == 'left':
            logo_x = 1.8 * cm
        elif pos == 'right':
            logo_x = w - logo_w - 1.8 * cm
        else: # center é o padrão
            logo_x = (w - logo_w) / 2
            
        logo_y = h - 3.2 * cm
        
        c.drawImage(
            logo_reader,
            logo_x, logo_y,
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
    c.setFillColor(primary_color)
    current_y -= 1.0 * cm
    c.drawCentredString(w / 2, current_y, full_name)
    
    # Linha 3: portador do CPF...
    c.setFont("Helvetica", 14)
    c.setFillColor(COLOR_TEXT)
    current_y -= 0.9 * cm
    c.drawCentredString(w / 2, current_y, f"portador do CPF {reg.cpf} concluiu com êxito o curso/treinamento")
    
    # Linha 4: Nome do Curso (Destaque)
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(primary_color)
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
    qr_size = 2.5 * cm
    qr_y = 1.1 * cm

    # Prepara os textos
    if empresa:
        raw_cnpj = "".join(filter(str.isdigit, empresa.cnpj or ""))
        doc_label = "CPF" if len(raw_cnpj) <= 11 else "CNPJ"
        company_text = f"{empresa.name} - {doc_label}: {empresa.cnpj or 'N/A'}"
    else:
        company_text = ""

    code_text = f"Código: {certificate.numeric_code_formatted}"
    url_text = certificate.verification_url
    
    # Calcula larguras para centralização total do bloco
    gap = 0.6 * cm
    max_text_w = max(
        c.stringWidth(company_text, "Helvetica", 10) if empresa else 0,
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
    
    if empresa:
        c.setFont("Helvetica", 10)
        c.setFillColor(COLOR_TEXT)
        c.drawString(text_x, qr_y + 1.6 * cm, company_text)

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(black)
    c.drawString(text_x, qr_y + 1.0 * cm, code_text)

    c.setFont("Helvetica", 7)
    c.drawString(text_x, qr_y + 0.5 * cm, url_text)

    c.save()
    return buf.getvalue()


def generate_preview_pdf(company, model_type) -> bytes:
    """Gera um PDF de demonstração com dados fictícios."""
    buf = io.BytesIO()
    w, h = landscape(A4)
    c = canvas.Canvas(buf, pagesize=landscape(A4))

    # Cores Locais
    primary_color = COLOR_PRIMARY
    secondary_color = COLOR_SECONDARY

    # Lógica de Fundo (Simulada)
    is_custom = model_type == 'custom' and company.custom_template
    
    if is_custom:
        template_path = Path(settings.MEDIA_ROOT) / str(company.custom_template)
        if template_path.exists():
            try:
                c.drawImage(str(template_path), 0, 0, width=w, height=h)
            except Exception:
                c.setFillColor(white)
                c.rect(0, 0, w, h, fill=1, stroke=0)
    else:
        primary_color = HexColor("#404040")
        secondary_color = HexColor("#A0A0A0")
        c.setFillColor(white)
        c.rect(0, 0, w, h, fill=1, stroke=0)
        c.setStrokeColor(secondary_color)
        c.setLineWidth(4)
        c.rect(0.8 * cm, 0.8 * cm, w - 1.6 * cm, h - 1.6 * cm, fill=0, stroke=1)

    # Lógica da Logo
    logo_reader = None
    if company.logo and company.logo_position != 'none':
        logo_path = Path(settings.MEDIA_ROOT) / str(company.logo)
        if logo_path.exists():
            try:
                logo_img = Image.open(logo_path)
                logo_reader = _pil_to_reader(logo_img)
            except Exception:
                pass
    
    if logo_reader:
        logo_w = 4 * cm
        logo_h = 2 * cm
        pos = company.logo_position
        if pos == 'left': logo_x = 1.8 * cm
        elif pos == 'right': logo_x = w - logo_w - 1.8 * cm
        else: logo_x = (w - logo_w) / 2
        logo_y = h - 3.2 * cm
        c.drawImage(logo_reader, logo_x, logo_y, width=logo_w, height=logo_h, preserveAspectRatio=True, mask="auto")

    # Título
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(w / 2, h - 7.5 * cm, "CERTIFICADO DE CONCLUSÃO")

    # Dados Fakes
    full_name = "NOME DO PARTICIPANTE DE TESTE"
    course_name_text = "TREINAMENTO DE DEMONSTRAÇÃO"
    date_string = "01/01/2026"
    local_text = f"Local: INSTITUIÇÃO DE TESTE realizado em {date_string} - SUA CIDADE / UF."
    workload_str = "10h"
    
    current_y = h - 8.23 * cm
    c.setFont("Helvetica", 14); c.setFillColor(COLOR_TEXT); c.drawCentredString(w / 2, current_y, "Certificamos que")
    current_y -= 1.0 * cm
    c.setFont("Helvetica-Bold", 24); c.setFillColor(primary_color); c.drawCentredString(w / 2, current_y, full_name)
    current_y -= 0.9 * cm
    c.setFont("Helvetica", 14); c.setFillColor(COLOR_TEXT); c.drawCentredString(w / 2, current_y, f"portador do CPF 123.456.789-00 concluiu com êxito o curso/treinamento")
    current_y -= 1.1 * cm
    c.setFont("Helvetica-Bold", 20); c.setFillColor(primary_color); c.drawCentredString(w / 2, current_y, course_name_text)
    current_y -= 0.9 * cm
    c.setFont("Helvetica", 12); c.setFillColor(COLOR_TEXT); c.drawCentredString(w / 2, current_y, local_text)
    current_y -= 0.7 * cm
    c.setFont("Helvetica", 14); c.setFillColor(black); c.drawCentredString(w / 2, current_y, f"Carga Horária: {workload_str}.")

    # Assinatura Fake
    footer_y = 5 * cm
    sig_width = 6 * cm
    current_x = (w - sig_width) / 2
    c.setStrokeColor(black); c.setLineWidth(0.5); c.line(current_x, footer_y - 0.2 * cm, current_x + sig_width, footer_y - 0.2 * cm)
    c.setFont("Helvetica-Bold", 10); c.drawCentredString(current_x + (sig_width / 2), footer_y - 0.6 * cm, "NOME DO INSTRUTOR")
    c.setFont("Helvetica", 9); c.drawCentredString(current_x + (sig_width / 2), footer_y - 1.0 * cm, "Instrutor Responsável")

    # Rodapé Fake
    qr_size = 2.5 * cm; qr_y = 1.1 * cm; gap = 0.6 * cm
    company_text = f"{company.name} - CNPJ: 00.000.000/0001-00"
    code_text = "Código: 0000 0000 0000"
    url_text = "https://fbonin.cloud"
    total_block_width = qr_size + gap + max(c.stringWidth(company_text, "Helvetica", 10), c.stringWidth(code_text, "Helvetica-Bold", 8), c.stringWidth(url_text, "Helvetica", 7))
    block_start_x = (w - total_block_width) / 2

    qr_img = _qr_image(url_text)
    qr_reader = _pil_to_reader(qr_img)
    c.drawImage(qr_reader, block_start_x, qr_y, width=qr_size, height=qr_size)
    text_x = block_start_x + qr_size + gap
    c.setFont("Helvetica", 10); c.setFillColor(COLOR_TEXT); c.drawString(text_x, qr_y + 1.6 * cm, company_text)
    c.setFont("Helvetica-Bold", 8); c.setFillColor(black); c.drawString(text_x, qr_y + 1.0 * cm, code_text)
    c.setFont("Helvetica", 7); c.drawString(text_x, qr_y + 0.5 * cm, url_text)

    c.save()
    return buf.getvalue()

