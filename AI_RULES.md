# AI_RULES.md — Regras Absolutas para o Gemini CLI

> **Leia este arquivo ANTES de qualquer intervenção no código.**
> Estas regras existem para evitar alucinações, sobrescritas acidentais
> e criação de funcionalidades não solicitadas.

---

## 1. REGRA DE OURO — Faça APENAS o que foi pedido

- Se o usuário pedir "corrija o bug X", corrija **somente** o bug X.
- Se o usuário pedir "adicione o campo Y ao formulário", adicione **somente** esse campo.
- **Nunca** refatore, reorganize ou renomeie código que não foi mencionado na tarefa.
- **Nunca** crie arquivos, funções, classes ou views adicionais sem solicitação explícita.
- **Nunca** remova código existente sem solicitação explícita.

---

## 2. PILHA TECNOLÓGICA — NÃO substitua, NÃO "melhore"

| Camada | Tecnologia escolhida | Proibido substituir por |
|---|---|---|
| Framework | **Django 5.0** | FastAPI, Flask, DRF (sem pedido) |
| Linguagem | **Python 3.12** | Qualquer outra |
| Geração de PDF | **ReportLab** | WeasyPrint, xhtml2pdf, Puppeteer |
| QR Code | **qrcode[pil]** | segno, pyqrcode |
| WhatsApp | **WAHA API** | Twilio, Evolution API, outros |
| Tarefas assíncronas | **Celery + Redis** | Dramatiq, RQ, threading manual |
| Frontend | **Bootstrap 5 via CDN** | React, Vue, Tailwind (sem pedido) |
| Banco de dados dev | **SQLite** | PostgreSQL (exceto se pedido para prod) |
| Servidor de arquivos estáticos | **WhiteNoise** | Nginx, S3 (exceto se pedido) |

---

## 3. ESTRUTURA DE ARQUIVOS — Não mova, não renomeie

```
certificados/
├── config/                  ← configurações Django
│   ├── settings/
│   │   ├── base.py          ← configurações compartilhadas
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py
├── apps/
│   ├── core/                ← modelos Company, Instructor
│   ├── registrations/       ← formulário do aluno, model Registration
│   └── certificates/        ← model Certificate, painel, verificação, PDF
│       └── services/        ← pdf_generator, email_sender, whatsapp_sender, certificate_service
├── templates/
│   ├── base.html
│   ├── registrations/
│   ├── certificates/
│   └── emails/
├── static/
├── media/                   ← ignorado pelo git, gerado em runtime
├── .env                     ← NUNCA commitar
├── .env
├── requirements.txt
├── manage.py
├── AI_RULES.md              ← este arquivo
└── CURRENT_STATE.md         ← estado atual do projeto
```

**Proibido:**
- Mover apps para fora de `apps/`
- Criar um `services.py` na raiz de `apps/certificates/` (use `services/certificate_service.py`)
- Renomear `admin_panel.html` para outro nome

---

## 4. MODELOS DE DADOS — Fluxo obrigatório

```
Registration (apps/registrations)
    │ OneToOne
    ▼
Certificate (apps/certificates)
    │ ForeignKey (via Registration)
    ▼
Instructor → Company (apps/core)
```

- `Registration.status` só tem dois valores: `pending` | `sent`
- `Certificate.numeric_code` é gerado automaticamente, **nunca** editável pelo usuário
- O `Certificate` só é criado quando o responsável clica em "Enviar Certificado"

---

## 5. FLUXO DE NEGÓCIO — Nunca altere sem pedido

```
[Aluno] → preenche formulário → Registration(status=pending) salvo
[Responsável] → painel → vê lista → clica "Enviar Certificado"
[Sistema] → issue_certificate_task.delay(reg_id)
         → certificate_service.issue_certificate()
              ↓ pdf_generator.generate_certificate_pdf()
              ↓ certificate.pdf_file.save()
              ↓ email_sender.send_certificate_email()
              ↓ whatsapp_sender.send_certificate_whatsapp()
              ↓ Registration.status = "sent"
[Qualquer pessoa] → /painel/verificar/<codigo>/ → verifica autenticidade
```

---

## 6. AUTENTICAÇÃO E AUTORIZAÇÃO

- O painel (`/painel/`) exige login Django padrão (`@login_required`)
- O formulário de inscrição (`/`) e a verificação (`/painel/verificar/`) são **públicos**
- **Não implemente** JWT, OAuth, ou sistemas de auth customizados sem pedido

---

## 7. VARIÁVEIS DE AMBIENTE — Lista oficial

Variáveis válidas (ver `.env.example`):
`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DJANGO_SETTINGS_MODULE`,
`DATABASE_URL`, `EMAIL_*`, `DEFAULT_FROM_EMAIL`,
`WAHA_BASE_URL`, `WAHA_API_KEY`, `WAHA_SESSION`, `WAHA_SENDER_NUMBER`,
`COMPANY_NAME`, `COMPANY_LOGO_URL`, `CERTIFICATE_BASE_URL`,
`REDIS_URL`, `CSRF_TRUSTED_ORIGINS`, `SECURE_SSL_REDIRECT`

**Nunca** adicione novas variáveis de ambiente sem atualizar `.env.example`.

---

## 8. DEPENDÊNCIAS — requirements.txt é a fonte da verdade

- Antes de usar qualquer biblioteca, verifique se está em `requirements.txt`
- Para adicionar uma dependência, inclua no `requirements.txt` E justifique no `CURRENT_STATE.md`
- **Nunca** use `pip install` diretamente sem atualizar `requirements.txt`

---

## 9. GERAÇÃO DO PDF — Regras do layout

O PDF usa **ReportLab** com layout A4 Paisagem. O arquivo de referência é:
`apps/certificates/services/pdf_generator.py`

Elementos obrigatórios no certificado (não remova nenhum):
1. Logo da empresa (via `settings.COMPANY_LOGO_URL`)
2. Nome completo do participante
3. Nome do treinamento
4. CPF do participante
5. Carga horária
6. Cidade e estado do treinamento
7. Nome, credenciais e assinatura do instrutor
8. QR Code (aponta para `CERTIFICATE_BASE_URL/painel/verificar/<codigo>/`)
9. Código numérico único (12 dígitos)
10. URL de verificação impressa

---

## 10. COMO RESPONDER A PEDIDOS AMBÍGUOS

Se não tiver certeza do que o usuário quer:
1. **Pergunte** antes de escrever código
2. Liste as opções e aguarde confirmação
3. Nunca assuma e implemente "o que parece melhor"

---

## 11. APÓS CADA MUDANÇA — Atualize CURRENT_STATE.md

Toda alteração deve ser registrada em `CURRENT_STATE.md`:
- O que foi alterado
- Por quê
- Data
- Qual arquivo foi modificado

---

## 12. PROIBIÇÕES ABSOLUTAS (NUNCA FAÇA ISSO)

❌ Nunca reescreva um arquivo inteiro quando apenas uma parte precisa mudar  
❌ Nunca delete migrations existentes  
❌ Nunca faça commit do arquivo `.env`  
❌ Nunca mude `numeric_code` para UUID ou outro formato  
❌ Nunca implemente autenticação por token sem solicitação  
❌ Nunca substitua Celery por `threading` ou `asyncio` manual  
❌ Nunca altere o layout do PDF sem solicitação explícita  
❌ Nunca crie uma API REST sem solicitação  
❌ Nunca instale ou sugira React/Vue/Next.js

#### 13. REGRAS PARA NOVAS FUNCIONALIDADES (Expansão)
*   **Link Generator:** Não crie um model "Event" ou "Training". Use uma View utilitária (`LinkGeneratorView`) que apenas ajuda o admin a construir a URL com Query Parameters.
*   **Vínculo de Instrutor:** O `instructor_id` deve ser passado via URL (GET) para o formulário de inscrição e salvo ocultamente no model `Registration`.
*   **Ações em Massa:** A emissão em massa deve ser feita iterando sobre o QuerySet filtrado e disparando a task do Celery para cada item individualmente. Não crie uma task monolítica.
