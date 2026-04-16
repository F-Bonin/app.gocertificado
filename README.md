# 🎓 GoCertificado

Sistema de Gestão, Operação e Certificação de Eventos como Curso, Treinamento, Workshop, Palestra, Congresso, ou qualquer outro evento, seja promovido por pessoa física ou instituições, que desejam realizar eventos organizados e seguros que geram impacto real na experiência do participante, com processos tecnologicos, automações de ponta a ponta, da inscrição à geração e envio de certificados, com QR Code e código numérico com sistema anti-fraude, com as melhores práticas de compliance, auditoria e garatina de segurança e autenticidade.

---

## ✨ Funcionalidades

- **Formulário de inscrição** público para participantes
- **Painel do responsável** com lista de participantes e botão "Enviar Certificado"
- **Geração de PDF** profissional com layout personalizado (ReportLab)
- **Envio por e-mail** com PDF anexado (Gmail SMTP gratuito)
- **Envio por WhatsApp** com texto + PDF (WAHA API)
- **QR Code** + código numérico único para verificação de autenticidade
- **Página de verificação** pública e acessível

---

## 🛠️ Stack Tecnológica

| Componente | Tecnologia |
|---|---|
| Backend | Python 3.12 + Django 5.0 |
| PDF | ReportLab |
| WhatsApp | WAHA (API não oficial) |
| Filas | Celery + Redis |
| Frontend | Bootstrap 5 (CDN) |
| Banco dev | SQLite |
| Banco prod | PostgreSQL (Neon.tech — free tier) |
| Deploy | Railway / Render (free tier) |
| Estáticos | WhiteNoise |

---

## 🚀 Rodando localmente

```bash
# 1. Clone e configure
git clone <repo>
cd certificados
cp .env.example .env
# Edite o .env

# 2. Ambiente Python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Banco de dados
python manage.py makemigrations core registrations certificates
python manage.py migrate
python manage.py createsuperuser

# 4. Serviços de suporte (Redis + WAHA via Docker)
docker compose up -d

# 5. Servidor Django
python manage.py runserver

# 6. Worker Celery (em outro terminal)
celery -A config worker -l info
```

---

## 📋 Fluxo do sistema

```
Aluno → Formulário (/) → Registration salva (status: pending)
         ↓
Responsável → Painel (/painel/) → Vê lista → Clica "Enviar Certificado"
         ↓
Celery Task → Gera PDF → Salva no banco
           → Envia por e-mail
           → Envia por WhatsApp
           → Registration.status = "sent"
         ↓
Qualquer pessoa → /painel/verificar/<codigo>/ → Verifica autenticidade
```

---

## 📁 Estrutura do projeto

```
certificados/
├── config/              ← settings, urls, celery, wsgi
├── apps/
│   ├── core/            ← Company, Instructor
│   ├── registrations/   ← formulário, model Registration
│   └── certificates/    ← PDF, e-mail, WhatsApp, verificação
│       └── services/
├── templates/
├── static/
├── AI_RULES.md          ← guia para Gemini CLI
├── CURRENT_STATE.md     ← estado atual do projeto
├── docker-compose.yml   ← Redis + WAHA
└── requirements.txt
```

---

## 🔍 Verificação de autenticidade

Qualquer pessoa pode verificar um certificado em:

```
https://seudominio.com.br/painel/verificar/<codigo-de-12-digitos>/
```

Ou pelo formulário em `/painel/verificar/`.

---

## 📄 Licença

Projeto privado. Todos os direitos reservados.
