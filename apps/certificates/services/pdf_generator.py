import io
import qrcode
import textwrap
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

COLOR_PRIMARY = HexColor("#1a3a5c")
COLOR_SECONDARY = HexColor("#c8a45a")
COLOR_TEXT = HexColor("#2d2d2d")

def _qr_image(url: str) -> Image.Image:
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")

def _pil_to_reader(img: Image.Image) -> ImageReader:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)

def _get_theme_color(color_choice):
    if color_choice == 'blue':
        return HexColor("#1a3a5c")
    elif color_choice == 'red':
        return HexColor("#b30000")
    return HexColor("#6c757d") # Cinza elegante

def generate_certificate_pdf(certificate) -> bytes:
    reg = certificate.registration
    course = reg.course
    empresa = reg.instructor.company if (reg.instructor and reg.instructor.company) else (course.company if (course and course.company) else None)

    buf = io.BytesIO()
    w, h = landscape(A4)
    c = canvas.Canvas(buf, pagesize=landscape(A4))

    template = course.certificate_template if course else None
    is_custom = template is not None

    if is_custom:
        background = template.background_image
        if background:
            template_path = Path(settings.MEDIA_ROOT) / str(background)
            if template_path.exists():
                try:
                    c.drawImage(str(template_path), 0, 0, width=w, height=h)
                except Exception:
                    c.setFillColor(white)
                    c.rect(0, 0, w, h, fill=1, stroke=0)
    else:
        # Modelo Padrão Dinâmico (Borda Dupla)
        color_choice = getattr(empresa, 'default_certificate_color', 'gray') if empresa else 'gray'
        theme_color = _get_theme_color(color_choice)

        c.setFillColor(white)
        c.rect(0, 0, w, h, fill=1, stroke=0)

        # Borda Dupla (Externa espessa, Interna fina)
        c.setStrokeColor(theme_color)
        c.setLineWidth(3)
        c.rect(0.8 * cm, 0.8 * cm, w - 1.6 * cm, h - 1.6 * cm, fill=0, stroke=1)
        c.setLineWidth(1)
        c.rect(0.9 * cm, 0.9 * cm, w - 1.8 * cm, h - 1.8 * cm, fill=0, stroke=1)

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
        logo_w = 6.5 * cm
        logo_h = 3.5 * cm
        pos = empresa.logo_position
        if pos == 'left': logo_x = 1.8 * cm
        elif pos == 'right': logo_x = w - logo_w - 1.8 * cm
        else: logo_x = (w - logo_w) / 2
        logo_y = h - 5.6 * cm
        c.drawImage(logo_reader, logo_x, logo_y, width=logo_w, height=logo_h, preserveAspectRatio=True, mask="auto")

    if is_custom:
        custom_title = template.title or empresa.custom_title
        if custom_title:
            c.setFillColor(COLOR_PRIMARY)
            c.setFont("Helvetica-Bold", 24)
            c.drawCentredString(w / 2, 420, custom_title)
    else:
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 32)
        c.drawCentredString(w / 2, 420, "CERTIFICADO DE CONCLUSÃO")

    if is_custom:
        y = 395
        c.setFillColor(COLOR_TEXT)
        c.setFont("Helvetica", 14)
        t1 = template.text_1 or empresa.custom_text_1
        t2 = template.text_2 or empresa.custom_text_2
        t3 = template.text_3 or empresa.custom_text_3
        t4 = template.text_4 or empresa.custom_text_4
        t5 = template.text_5 or empresa.custom_text_5
        t6 = template.text_6 or empresa.custom_text_6

        if t1:
            c.drawCentredString(w / 2, y, t1)
        y -= 0.7 * cm
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(COLOR_PRIMARY)
        c.drawCentredString(w / 2, y, (reg.full_name or "").upper())
        y -= 0.9 * cm
        c.setFont("Helvetica", 14)
        c.setFillColor(COLOR_TEXT)
        linha_2 = f"{t2 or ''} {reg.cpf} {t3 or ''}".strip()
        if linha_2:
            c.drawCentredString(w / 2, y, linha_2)
        y -= 0.9 * cm
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(COLOR_PRIMARY)
        course_name_str = (reg.course.name if (reg.course and reg.course.name) else (reg.course_name or "Treinamento não informado")).upper()
        c.drawCentredString(w / 2, y, course_name_str)
        y -= 0.9 * cm
        c.setFont("Helvetica", 14)
        c.setFillColor(COLOR_TEXT)
        course_dt = reg.course.start_date if (reg.course and reg.course.start_date) else reg.course_date
        data_str = course_dt.strftime('%d/%m/%Y') if course_dt else "Data não informada"
        linha_4 = f"{t4 or ''} {data_str}".strip()
        if linha_4:
            c.drawCentredString(w / 2, y, linha_4)
        y -= 0.9 * cm
        c.setFont("Helvetica", 14)
        if t5:
            linhas_texto_5 = textwrap.wrap(t5, width=90)
            for linha in linhas_texto_5:
                c.drawCentredString(w / 2, y, linha)
                y -= 0.6 * cm
        y -= 0.2 * cm
        c.setFont("Helvetica", 14)
        course_hrs = reg.course.hours if (reg.course and reg.course.hours) else reg.course_workload
        workload_str = f"{course_hrs}h" if course_hrs else "Carga horária não informada"
        linha_6 = f"{t6 or ''} {workload_str}".strip()
        if linha_6:
            c.drawCentredString(w / 2, y, linha_6)
        y -= 0.9 * cm
    else:
        # Texto Padrão Rigoroso (Preto e Linha Temática)
        c.setFillColor(black)
        c.setFont("Helvetica", 13)
        c.drawCentredString(w / 2, 380, "Certificamos que")

        c.setFont("Helvetica-Bold", 26)
        c.setFillColor(black)
        c.drawCentredString(w / 2, 300, (reg.full_name or "").upper())

        # Linha decorativa abaixo do nome na cor do tema
        c.setStrokeColor(theme_color)
        c.setLineWidth(1.5)
        name_w = c.stringWidth((reg.full_name or "").upper(), "Helvetica-Bold", 26)
        line_x = (w - name_w) / 2
        c.line(line_x, 300 - 4, line_x + name_w, 300 - 4)

        c.setFont("Helvetica", 13)
        c.setFillColor(black)
        linha_3 = f"portador do CPF: {reg.cpf}, concluiu com êxito o treinamento/Curso/Imersão"
        c.drawCentredString(w / 2, 260, linha_3)

        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(black)
        course_name_display = (reg.course.name if (reg.course and reg.course.name) else (reg.course_name or "Treinamento não informado")).upper()
        course_hrs_val = reg.course.hours if (reg.course and reg.course.hours) else reg.course_workload
        workload_display = f"{course_hrs_val}h" if course_hrs_val else "Carga horária não informada"
        linha_4 = f"{course_name_display} — Carga Horária: {workload_display}"
        c.drawCentredString(w / 2, 225, linha_4)

        c.setFont("Helvetica", 12)
        c.setFillColor(black)
        city_display = reg.course.city if (reg.course and reg.course.city) else "Cidade não informada"
        state_display = reg.course.state if (reg.course and reg.course.state) else "UF"
        course_dt_val = reg.course.start_date if (reg.course and reg.course.start_date) else reg.course_date
        data_str = course_dt_val.strftime('%d/%m/%Y') if course_dt_val else "Data não informada"
        linha_5 = f"realizado em {city_display}/{state_display} em {data_str}."
        c.drawCentredString(w / 2, 195, linha_5)

    # ── Assinaturas (Rodapé Dinâmico) ─────────────────────────────
    signatures = []
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
                        c.drawImage(sig_reader, current_x, footer_y - 0.7 * cm, width=sig_width, height=2 * cm, preserveAspectRatio=True, mask="auto")
                    except Exception:
                        pass
            
            # Linha da assinatura sempre preta
            c.setStrokeColor(black)
            c.setLineWidth(0.5)
            c.line(current_x, footer_y - 0.2 * cm, current_x + sig_width, footer_y - 0.2 * cm)
            c.setFont("Helvetica-Bold", 10)
            # Para o Default, a cor de fonte base é preta, então definimos explicitamente
            c.setFillColor(black)
            c.drawCentredString(current_x + (sig_width / 2), footer_y - 0.6 * cm, sig.full_name)
            c.setFont("Helvetica", 9)
            role_text = sig.role or sig.credentials
            c.drawCentredString(current_x + (sig_width / 2), footer_y - 1.0 * cm, role_text)

    # Rodapé Integrado (QR Code + Dados da Empresa)
    qr_size = 2.5 * cm
    qr_y = 1.1 * cm
    if empresa:
        raw_cnpj = "".join(filter(str.isdigit, empresa.cnpj or ""))
        doc_label = "CPF" if len(raw_cnpj) <= 11 else "CNPJ"
        company_text = f"{empresa.name} - {doc_label}: {empresa.cnpj or 'N/A'}"
    else:
        company_text = ""
    code_text = f"Código: {certificate.numeric_code_formatted}"
    url_text = certificate.verification_url

    gap = 0.6 * cm
    max_text_w = max(
        c.stringWidth(company_text, "Helvetica", 10) if empresa else 0,
        c.stringWidth(code_text, "Helvetica-Bold", 8),
        c.stringWidth(url_text, "Helvetica", 7)
    )
    total_block_width = qr_size + gap + max_text_w
    block_start_x = (w - total_block_width) / 2

    qr_img = _qr_image(certificate.verification_url)
    qr_reader = _pil_to_reader(qr_img)
    c.drawImage(qr_reader, block_start_x, qr_y, width=qr_size, height=qr_size)

    text_x = block_start_x + qr_size + gap
    if empresa:
        c.setFont("Helvetica", 10)
        c.setFillColor(black)
        c.drawString(text_x, qr_y + 1.6 * cm, company_text)
    
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(black)
    c.drawString(text_x, qr_y + 1.0 * cm, code_text)
    c.setFont("Helvetica", 7)
    c.drawString(text_x, qr_y + 0.5 * cm, url_text)

    c.save()
    return buf.getvalue()


def generate_preview_pdf(company, model_type, template=None, color=None) -> bytes:
    buf = io.BytesIO()
    w, h = landscape(A4)
    c = canvas.Canvas(buf, pagesize=landscape(A4))

    background = template.background_image if template else company.custom_template
    is_custom = model_type == 'custom' and background

    if is_custom:
        template_path = Path(settings.MEDIA_ROOT) / str(background)
        if template_path.exists():
            try:
                c.drawImage(str(template_path), 0, 0, width=w, height=h)
            except Exception:
                c.setFillColor(white)
                c.rect(0, 0, w, h, fill=1, stroke=0)
    else:
        # Preview do Modelo Padrão Dinâmico
        color_choice = color if color else getattr(company, 'default_certificate_color', 'gray')
        theme_color = _get_theme_color(color_choice)

        c.setFillColor(white)
        c.rect(0, 0, w, h, fill=1, stroke=0)

        c.setStrokeColor(theme_color)
        c.setLineWidth(3)
        c.rect(0.8 * cm, 0.8 * cm, w - 1.6 * cm, h - 1.6 * cm, fill=0, stroke=1)
        c.setLineWidth(1)
        c.rect(0.9 * cm, 0.9 * cm, w - 1.8 * cm, h - 1.8 * cm, fill=0, stroke=1)

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
        logo_w = 6.5 * cm
        logo_h = 3.5 * cm
        pos = company.logo_position
        if pos == 'left': logo_x = 1.8 * cm
        elif pos == 'right': logo_x = w - logo_w - 1.8 * cm
        else: logo_x = (w - logo_w) / 2
        logo_y = h - 4.7 * cm
        c.drawImage(logo_reader, logo_x, logo_y, width=logo_w, height=logo_h, preserveAspectRatio=True, mask="auto")

    if model_type == 'custom':
        title_text = template.title if template else company.custom_title
        if title_text:
            c.setFillColor(COLOR_PRIMARY)
            c.setFont("Helvetica-Bold", 24)
            c.drawCentredString(w / 2, 420, title_text)
    else:
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 32)
        c.drawCentredString(w / 2, 420, "CERTIFICADO DE CONCLUSÃO")

    if model_type == 'custom':
        y = 395
        c.setFillColor(COLOR_TEXT)
        c.setFont("Helvetica", 14)
        t1 = template.text_1 if template else company.custom_text_1
        t2 = template.text_2 if template else company.custom_text_2
        t3 = template.text_3 if template else company.custom_text_3
        t4 = template.text_4 if template else company.custom_text_4
        t5 = template.text_5 if template else company.custom_text_5
        t6 = template.text_6 if template else company.custom_text_6

        if t1:
            c.drawCentredString(w / 2, y, t1)
        y -= 0.7 * cm
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(COLOR_PRIMARY)
        c.drawCentredString(w / 2, y, "NOME DO PARTICIPANTE DE TESTE")
        y -= 0.9 * cm
        c.setFont("Helvetica", 14)
        c.setFillColor(COLOR_TEXT)
        linha_2 = f"{t2 or ''} 123.456.789-00 {t3 or ''}".strip()
        if linha_2:
            c.drawCentredString(w / 2, y, linha_2)
        y -= 0.9 * cm
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(COLOR_PRIMARY)
        c.drawCentredString(w / 2, y, "TREINAMENTO DE DEMONSTRAÇÃO")
        y -= 0.9 * cm
        c.setFont("Helvetica", 14)
        c.setFillColor(COLOR_TEXT)
        linha_4 = f"{t4 or ''} 10/10/2026".strip()
        if linha_4:
            c.drawCentredString(w / 2, y, linha_4)
        y -= 0.9 * cm
        c.setFont("Helvetica", 14)
        if t5:
            linhas_texto_5 = textwrap.wrap(t5, width=90)
            for linha in linhas_texto_5:
                c.drawCentredString(w / 2, y, linha)
                y -= 0.6 * cm
        y -= 0.2 * cm
        c.setFont("Helvetica", 14)
        linha_6 = f"{t6 or ''} 10h".strip()
        if linha_6:
            c.drawCentredString(w / 2, y, linha_6)
        y -= 0.9 * cm
    else:
        # Texto Padrão Rigoroso (Preview)
        c.setFillColor(black)
        c.setFont("Helvetica", 13)
        c.drawCentredString(w / 2, 380, "Certificamos que")

        c.setFont("Helvetica-Bold", 26)
        c.setFillColor(black)
        c.drawCentredString(w / 2, 300, "NOME DO PARTICIPANTE DE TESTE")

        c.setStrokeColor(theme_color)
        c.setLineWidth(1.5)
        name_w = c.stringWidth("NOME DO PARTICIPANTE DE TESTE", "Helvetica-Bold", 26)
        line_x = (w - name_w) / 2
        c.line(line_x, 300 - 4, line_x + name_w, 300 - 4)

        c.setFont("Helvetica", 13)
        c.setFillColor(black)
        linha_3 = "portador do CPF: 123.456.789-00, concluiu com êxito o treinamento/Curso/Imersão"
        c.drawCentredString(w / 2, 260, linha_3)

        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(black)
        linha_4 = "TREINAMENTO DE DEMONSTRAÇÃO — Carga Horária: 10h"
        c.drawCentredString(w / 2, 225, linha_4)

        c.setFont("Helvetica", 12)
        c.setFillColor(black)
        linha_5 = "realizado em SUA CIDADE / UF em 10/10/2026."
        c.drawCentredString(w / 2, 195, linha_5)

    footer_y = 5 * cm
    sig_width = 6 * cm
    current_x = (w - sig_width) / 2
    c.setStrokeColor(black); c.setLineWidth(0.5); c.line(current_x, footer_y - 0.2 * cm, current_x + sig_width, footer_y - 0.2 * cm)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 10); c.drawCentredString(current_x + (sig_width / 2), footer_y - 0.6 * cm, "NOME DO INSTRUTOR")
    c.setFont("Helvetica", 9); c.drawCentredString(current_x + (sig_width / 2), footer_y - 1.0 * cm, "Instrutor Responsável")

    qr_size = 2.5 * cm; qr_y = 1.1 * cm; gap = 0.6 * cm
    company_text = f"{company.name} - CNPJ: 00.000.000/0001-00"
    code_text = "Código: 0000 0000 0000"
    url_text = "gocertificado.com"
    
    total_block_width = qr_size + gap + max(c.stringWidth(company_text, "Helvetica", 10), c.stringWidth(code_text, "Helvetica-Bold", 8), c.stringWidth(url_text, "Helvetica", 7))
    block_start_x = (w - total_block_width) / 2
    qr_img = _qr_image(url_text)
    qr_reader = _pil_to_reader(qr_img)
    c.drawImage(qr_reader, block_start_x, qr_y, width=qr_size, height=qr_size)

    text_x = block_start_x + qr_size + gap
    c.setFont("Helvetica", 10); c.setFillColor(black); c.drawString(text_x, qr_y + 1.6 * cm, company_text)
    c.setFont("Helvetica-Bold", 8); c.setFillColor(black); c.drawString(text_x, qr_y + 1.0 * cm, code_text)
    c.setFont("Helvetica", 7); c.drawString(text_x, qr_y + 0.5 * cm, url_text)

    c.save()
    return buf.getvalue()
