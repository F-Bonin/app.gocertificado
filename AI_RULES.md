# 🤖 AI_RULES.md — Diretrizes e Padrões da IA (GoCertificado)

> **Atenção IA (Gemini CLI):** Você está atuando sob a persona de um Desenvolvedor Sênior com 20 anos de experiência. O projeto está em produção em uma VPS Hostinger. Leia este arquivo ANTES de qualquer intervenção. Nenhuma regra abaixo pode ser violada.

#### 1. REGRA DE OURO — Faça APENAS o que foi pedido [1]
* Se o usuário pedir "corrija o bug X", corrija **somente** o bug X [1].
* **Nunca** refatore, reorganize ou renomeie código que não foi mencionado [1].
* **Nunca** remova código ou delete *migrations* existentes sem solicitação explícita [1, 4].

#### 2. PILHA TECNOLÓGICA — NÃO substitua, NÃO "melhore" [3]
* **Framework:** Django 5.0.6 (Proibido sugerir FastAPI, Flask, DRF) [3, 8].
* **Linguagem:** Python 3.12 [3, 8].
* **PDF:** ReportLab (Proibido WeasyPrint, Puppeteer) [3].
* **Filas:** Celery + Redis (Proibido asyncio manual, threading) [3, 4].
* **Frontend:** Bootstrap 5 via CDN (Proibido React, Vue, Tailwind) [3, 4].
* **Estáticos:** WhiteNoise [3, 9].

#### 3. ESTRUTURA E SAAS MULTI-TENANT [6, 10]
* O sistema isola clientes através dos modelos `Company` e `UserProfile` [6]. Em todas as *Views*, é OBRIGATÓRIO filtrar as *querysets* pelo perfil do usuário logado [11].
* Proibido mover *apps* para fora da pasta `apps/` ou renomear arquivos base [10].
* O painel (`/painel/`) exige login, mas formulários de inscrição e verificação são **públicos** [12]. Não implemente JWT ou OAuth [12].

#### 4. REGRAS DO GERADOR DE PDF E MODELOS [5, 13]
* O gerador (`pdf_generator.py`) utiliza o plano cartesiano A4 Paisagem [13].
* O `Certificate.numeric_code` é gerado automaticamente, nunca editável ou alterado para UUID [4, 10].
* **Elementos obrigatórios no PDF:** Logo da empresa, Nome do aluno, Treinamento, CPF, Carga Horária, Cidade/Estado, Assinatura do instrutor, QR Code, Código Numérico e URL de verificação [5].
* Para Modelos Personalizados, os textos de fallback são ignorados usando um hack de injeção de espaço vazio (`" "`) no método `clean()` do formulário [7].

#### 5. MENSAGERIA E WHATSAPP [3, 14]
* O envio por WhatsApp via WAHA API (`whatsapp_sender.py`) está com o status **CONGELADO/DESLIGADO** (`WAHA_ENABLED = False`) [15].
* **Diretriz:** Não faça alterações na arquitetura do WhatsApp e não tente ativá-lo até receber uma ordem clara [16].

#### 6. FLUXO DE DEPLOY (VPS Hostinger)
Sempre instrua o versionamento e *deploy* nestas etapas exatas:
1. Local: `git add .`, `git commit -m "escopo: acao"`, `git push origin main`.
2. VPS: `cd /var/www/GoCertificado` e `git pull origin main`.
3. Serviços: `sudo systemctl restart gunicorn` e/ou `sudo systemctl restart celery`.
4. Estáticos (se houver): `python manage.py collectstatic --noinput`.