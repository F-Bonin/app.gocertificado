# CURRENT_STATE.md — Estado Atual do Projeto

> **Atualize este arquivo após cada sessão de desenvolvimento.**
> O Gemini CLI deve ler este arquivo para entender onde o projeto está
> antes de qualquer intervenção.

---

## 🗓️ Última atualização: 2026-04-02 (Correção de Bug: NoneType no Email Service)

---

## ✅ O que já está implementado

### Estrutura Base
- [x] Estrutura de diretórios completa
- [x] Configurações de ambiente (`base.py`, `development.py`, `production.py`, `.env`)
- [x] URLs com namespace e Celery configurado
- [x] Arquivos `apps.py` e `context_processor` (nome/logo da empresa)
- [x] **Arquitetura SaaS Multitenant** (Login, Registro e Perfil vinculados a Empresas)

### App `accounts`
- [x] Model `UserProfile` com vínculo a `Company` (SaaS Multi-tenancy)
- [x] Formulário de registro customizado `UserRegistrationForm`
- [x] Views de Registro (com criação automática de empresa), Login e Logout
- [x] Templates de login e registro em Bootstrap 5
- [x] Migrações aplicadas e rotas configuradas em `/accounts/`

### App `core`
- [x] Models `Company`, `Instructor` e `Course`
- [x] Dados de teste iniciais criados via shell
- [x] Gestão SaaS de Empresa (Edição de Perfil e Logo)
- [x] CRUD SaaS de Instrutores (Isolamento por empresa)
- [x] **Gestão de Treinamentos (Fase 6.1):** CRUD completo, Clonagem e Geração de Link Único (UUID) para inscrições.
- [x] **Blindagem do Frontend (Cadastro de Treinamentos):** Validação de datas cruzadas, toggle dinâmico de assinaturas e Modal de confirmação seguro (Fake Button).

### App `registrations`
- [x] Model `Registration` vinculado à entidade `Course` (Fase 6.1)
- [x] `RegistrationForm` com campos de perfil (Gênero/Profissão) e injeção dinâmica de dados de treinamento no formulário público.
- [x] View de Inscrição segura (revertida para evitar emissão precoce via Celery).
- [x] Propriedade `cpf_masked` robustecida.
- [x] Trava de duplicidade (CPF + Course) para evitar inscrições repetidas no mesmo curso.

### App `certificates`
- [x] Model `Certificate` vinculado à empresa e à inscrição (SaaS).
- [x] **Central de Certificados 2.0:** Interface AJAX (Fetch) para envio e reset de status sem recarregar a página.
- [x] `VerifyCertificateView` atualizada para nova arquitetura de cursos.
- [x] Tarefa assíncrona Celery para emissão.
- [x] **Emissão em massa (Bulk Issue):** Integrada ao Celery via AJAX. [x]
- [x] **Interface Reativa:** Atualização de status em tempo real via AJAX Short Polling (sem reload). [x]
- [x] **Métricas do Dashboard:** Total de inscrições, emitidos e pendentes isolados por empresa. [x]
- [x] **View de Alunos/Participantes:** Listagem agrupada por CPF (Sanfona) com histórico de treinamentos. [x]

### Ativos e Templates
- [x] PDF Generator: QR Code reduzido e alinhado lateralmente com dados da empresa (Rodapé integrado).
- [x] Interface AJAX Toasts para feedback instantâneo no painel.
- [x] Templates base e e-mail responsivos atualizados para o novo modelo Course.
- [x] **Sidebar (Barra Lateral):** Limpeza e reordenação estratégica dos links. [x]

### Serviços (`apps/certificates/services/`)
- [x] `pdf_generator.py` — Geração profissional com ReportLab e assinaturas dinâmicas via Course.
- [x] `email_sender.py` — Assunto e corpo do e-mail vinculados ao nome do curso.
- [x] `whatsapp_sender.py` — **Refatorado**: Payload corrigido (chatId, text, session) para evitar erro 422 no WAHA.
- [x] `certificate_service.py` — Orquestração completa alinhada à arquitetura de Cursos.

---

## ⏳ O que ainda precisa ser feito (próximos passos)

### Prioridade MÉDIA
- [x] Criar comando de management para reenviar certificado com erro (ex: `python manage.py retry_certificates`)
- [x] Implementar exportação da lista de participantes para CSV no painel (Multitenant e vinculado ao Course)
- [ ] Refatorar o envio de WhatsApp via WAHA usando a rota oficial para PDFs em base64 (Melhoria de UX).

### Prioridade BAIXA
- [ ] Deploy em ambiente de homologação

---

## 🐛 Bugs conhecidos / Pendências técnicas

| # | Descrição | Arquivo | Status |
|---|---|---|---|
| 1 | `apps/core/apps.py` não criado | `apps/core/` | Resolvido |
| 2 | Falta `context_processor` para `COMPANY_NAME` | `config/settings/base.py` | Resolvido |
| 3 | `cpf_masked` robustez | `registrations/models.py` | Resolvido |
| 4 | `generate_certificate_pdf` fallback logo | `certificates/services/pdf_generator.py` | Resolvido |

---

## 🗒️ Histórico de Mudanças

| Data | Mudança | Feito por |
|---|---|---|
| 2025-02 | Arquitetura inicial criada | Fernando Bonin & Gemini CLI |
| 2026-02-18 | Estabilização inicial, criação de apps.py, context processor e testes de fluxo | Gemini CLI |
| 2026-02-19 | Implementação de Exportação CSV, Dashboard, AJAX Toasts e comando Retry | Gemini CLI |
| 2026-02-19 | Implementação do Fluxo de Gestão: Gerador de Links e Emissão em Massa | Gemini CLI |
| 2026-02-26 | Transformação completa para SaaS Multitenant (Autenticação, Dashboard, CRUDs e Gerador de Links) | Gemini CLI |
| 2026-02-26 | Atualização dos modelos Company e Registration para suportar nova identidade visual do PDF | Gemini CLI |
| 2026-02-26 | Refatoração do PDF Generator para aplicar identidade visual dinâmica (Logo e CNPJ) por empresa | Gemini CLI |
| 2026-02-26 | Refatoração do layout do PDF e correção do bug de data 'N/A' | Gemini CLI |
| 2026-02-28 | Refatoração da View de Inscrição e Form para salvar Data, Cidade e Estado via URL | Gemini CLI |
| 2026-02-28 | Implementação da Fase 6.1: Modelo Course, CRUD de Treinamentos, Clonagem e Links Únicos | Gemini CLI |
| 2026-02-28 | Implementação da Fase 6.2: Tela Meus Treinamentos, Filtros e Exportação CSV | Gemini CLI |
| 2026-02-28 | Adição de campos Gênero e Profissão no modelo de Inscrição e ajuste no fluxo de sucesso | Gemini CLI |
| 2026-03-04 | Transição completa da dependência de Inscrições e Certificados para a entidade Course | Gemini CLI |
| 2026-03-04 | Refatoração do envio de WhatsApp via WAHA (Correção erro 422 e estrutura de payload) | Gemini CLI |
| 2026-03-04 | Implementação de AJAX na Central de Certificados (Troca de botões sem reload e reset status) | Gemini CLI |
| 2026-03-04 | Blindagem do frontend no cadastro de Treinamentos (Validação cruzada, assinaturas e modal Fake Button) | Gemini CLI |
| 2026-03-04 | Ajustes finos no PDF: QR Code reduzido e rodapé integrado e centralizado | Gemini CLI |
| 2026-03-04 | Implementação de exclusão de inscrições via AJAX com confirmação nativa. | Gemini CLI |
| 2026-03-04 | Criação da view de Alunos/Participantes agrupada de forma absoluta por CPF. | Gemini CLI |
| 2026-03-04 | Criação do Dashboard de Métricas com status traduzidos via choices. | Gemini CLI |
| 2026-03-04 | Limpeza e reordenação estratégica da barra lateral (Sidebar). | Gemini CLI |
| 2026-03-04 | Implementação da exportação consolidada de alunos para CSV (Excel compatible) com isolamento SaaS. | Gemini CLI |
| 2026-03-04 | Tradução dos rótulos de status no Dashboard (Uso das labels oficiais do modelo). | Gemini CLI |
| 2026-03-04 | Implementação da funcionalidade de Envio em Massa (Bulk Issue) via AJAX com feedback visual. | Gemini CLI |
| 2026-03-04 | Implementada view e rota no backend para disparar múltiplas tarefas na fila do Celery baseadas nos filtros de tela. | Gemini CLI |
| 2026-03-04 | Construído motor de Polling assíncrono em Vanilla JS para atualizar status (Pendente -> Processando -> Enviado) e recriar botões de ação dinamicamente. | Gemini CLI |
| 2026-03-04 | Correção de bugs de DOM manipulation, isolando as mudanças de estado às células corretas da tabela. | Gemini CLI |
| 2026-03-04 | Atualização do roteamento raiz e LOGIN_REDIRECT_URL para apontarem para o novo Dashboard. | Gemini CLI |
| 2026-03-04 | Adicionada Feature Flag WAHA_ENABLED em settings.py e whatsapp_sender.py para habilitar/desabilitar disparos via WhatsApp. | Gemini CLI |
| 2026-03-09 | Sincronização da Página de Verificação com dados reais (Course/Instructor) e melhoria no select_related | Gemini CLI |
| 2026-03-09 | Adição de campos de Instituição nos modelos Registration e Course, atualização do formulário e gerador de links | Gemini CLI |
| 2026-03-09 | Refatoração da página pública de solicitação (form.html): nova disposição, logo e campos de treinamento somente leitura | Gemini CLI |
| 2026-03-09 | Atualização do layout de texto do PDF (6 linhas sequenciais) e tratamento de campos nulos de instituição | Gemini CLI |
| 2026-03-09 | Implementação dos campos de Local/Instituição no CRUD de Treinamentos e geração de URL com QueryString | Gemini CLI |
| 2026-03-09 | Reordenação visual dos campos de endereço no CRUD de Treinamentos (Cidade/Estado ao final) | Gemini CLI |
| 2026-03-09 | Atualização das listagens (Meus Treinamentos e Central de Certificados) para exibir Nome da Instituição na coluna Local | Gemini CLI |
| 2026-03-09 | Correção do caminho do logo na página pública (form.html) usando a tag static do Django | Gemini CLI |
| 2026-03-09 | Ajustes de layout no PDF do certificado (coordenadas Y e tamanhos de fonte) para evitar sobreposição | Gemini CLI |
| 2026-03-09 | Refinamento de coordenadas Y no PDF: deslocamento do bloco central (+40 pts) e da imagem da assinatura (-20 pts) para maior realismo | Gemini CLI |
| 2026-03-09 | Sintonia fina no eixo Y do texto central do PDF (-15 pts) para criar respiro entre título e corpo | Gemini CLI |
| 2026-03-10 | Ajuste de exibição do campo "Local" na página de verificação de certificado para incluir nome da instituição, cidade e estado. | Gemini CLI |
| 2026-03-10 | Substituição dos campos de Cidade e Estado no formulário de Treinamento (Course) por campos de texto com preenchimento automático ViaCEP, incluindo o campo CEP. | Gemini CLI |
| 2026-03-10 | Implementação de campos de endereço granulares (CEP, Rua, Número, Complemento, Bairro, Cidade, Estado) no formulário e modelo de Inscrição (Registration), com preenchimento automático ViaCEP. | Gemini CLI |
| 2026-04-02 | Correção de erro NoneType em `email_sender.py` (Safe extraction de `company_email` para o `reply_to`). | Gemini CLI |
| 2026-04-02 | Alteração da origem do Reply-To para `Company.objects.first()` em `email_sender.py`. | Gemini CLI |
| 2026-04-02 | Implementação de arquitetura Multi-Tenant para o Reply-To: extração dinâmica do e-mail via `Registration -> Course -> Company`. | Gemini CLI |
| 2026-04-03 | Adicionada obrigatoriedade aos campos 'name', 'start_date' e 'hours' no model Course para garantir integridade do certificado. | Gemini CLI |
| 2026-04-03 | Correção da injeção de variáveis no PDF: tratamento seguro para Carga Horária, Data e Nome do Treinamento para evitar 'Noneh' ou 'N/A'. | Gemini CLI |
| 2026-04-03 | Otimização da QuerySet em 'issue_certificate': Adicionado 'select_related("course", "instructor__company")' para garantir carregamento seguro dos dados de treinamento e empresa. | Gemini CLI |
| 2026-04-03 | Correção da persistência de inscrições: Implementado padrão 'commit=False' na RegistrationCreateView para garantir vínculo da FK 'course' no salvamento. | Gemini CLI |
