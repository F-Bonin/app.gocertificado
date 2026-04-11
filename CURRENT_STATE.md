# 📊 CURRENT_STATE.md — Estado Atual do Projeto

**Atualize este arquivo após cada sessão de desenvolvimento.** A IA deve ler este arquivo para entender o escopo completo.

#### 🗓️ Última atualização: 2026-04-11 (Correções de UX e Print Layout) [15]

---

#### ✅ O que já está implementado [6]
**Estrutura Base e SaaS:**
* [x] Arquitetura SaaS Multitenant (Login, Registro e Perfil vinculados a Empresas) [6, 11].
* [x] Models: `Company`, `Instructor`, `Course`, `Registration`, `Certificate`, `CertificateTemplate` [11, 17, 18].
* [x] **Refatoração de UX Copy:** Nomenclatura alterada de "Treinamento" para "Evento" em todo o painel administrativo, modelos e templates [9, 10].
* [x] **Padronização de Nomenclatura:** Termos de "Inscrição" alterados para "Solicitação de Certificado" em formulários de emissão [8].

**Correções e Refinamentos (Recente):**
* [x] **Mensagem de Sucesso de Inscrição:** Corrigida a lógica de exibição condicional no template para diferenciar Inscrição de Evento e Solicitação de Certificado [14].
* [x] **Tabela de Impressão (Bugfix):** Refatoração agressiva do CSS `@media print` para garantir o alinhamento perfeito de bordas e linhas na Lista de Presença em formato A4 [15].
* [x] **Layout de Impressão (UX):** O layout de impressão da Lista de Presença foi otimizado para formato Paisagem (Landscape) e implementada a classe `nowrap-print` para evitar quebras de linha nas colunas de identificação [16].
* [x] **Refinamento de Impressão (UX):** Layout de impressão da Lista de Presença refinado com a inclusão do campo Profissão ao lado do CPF e ajustes estruturais no campo de Assinatura (alinhamento e estilo de linha) [17].
* [x] **Bugfix de Layout de Impressão:** Corrigido o erro de bordas duplicadas e títulos cortados na tabela de impressão através do ajuste de `display: table-cell` para elementos exclusivos de impressão [18].

**Sistema de Inscrição e Solicitação (UX):**
* [x] **Diferenciação Visual de Sucesso:** Implementada lógica de sessão nas views e condicional no template `registration_success.html` para identificar se o usuário concluiu uma "Inscrição em Evento" ou uma "Solicitação de Certificado", exibindo mensagens personalizadas [14].
* [x] **Inscrição Pré-Evento:** Utilização dos campos `registration_start` e `registration_end` para controle de acesso ao formulário de inscrição [11].
* [x] **Lista de Presença Online (Check-in):** Implementada com sucesso a funcionalidade completa de check-in digital via AJAX e suporte a layout de impressão físico A4 [13].
* [x] **Lista de Presença Multitenant:** Implementada `EventPresenceListView` com filtragem rigorosa por empresa [12].
* [x] **Check-in Online (AJAX):** Implementada `TogglePresenceView` para alternância de status em tempo real sem reload [12].
* [x] **Interface Profissional (Frontend):** Template `presence_list.html` com suporte nativo a impressão (CSS `@media print`) [13].
* [x] **Atalho no Painel:** Adicionado botão de acesso rápido à Lista de Presença diretamente na listagem de eventos para facilitar o fluxo do usuário [13].
* [x] **Check-in Reativo:** JS nativo (Fetch API) com feedback visual via Toasts [13].
* [x] **Suporte a Lista Física:** Coluna de assinatura dedicada exclusiva para a versão impressa [13].
* [x] **Segurança:** Validação multi-tenant em todas as camadas (View e AJAX) [12].

**Sistema de Controle de Períodos e UX Reativa:**
* [x] **Cronômetro Reativo:** Implementada lógica Vanilla JS com `setInterval` para contagem regressiva em tempo real nos formulários de Inscrição e Solicitação de Certificado [12].
* [x] **Robustez do Cronômetro:** Refatoração do JS para lidar com datas de encerramento vazias (link vitalício), evitando erros `NaN` [13].
* [x] **Exibição Explícita de Datas:** Adicionado card `alert-info` no topo dos formulários públicos exibindo datas de início e encerramento formatadas (Django `|date`) [12].
* [x] **Correção de Formatação:** Implementada separação de filtros de data e hora no Django (`|date:"d/m/Y"` e `|date:"H:i"`) para garantir a exibição correta da palavra "às" e evitar o erro "à00" [14].
* [x] **Bloqueio Visual Dinâmico:** Ocultação automática do formulário (`display: none`) e exibição de status "Abre em", "Expira em" ou "Encerrado" baseada no horário do cliente sincronizado com o servidor [12].
* [x] **UX de Erro Temporal:** Refatoração do backend (`dispatch`) para renderizar template elegante (`time_locked.html`) em vez de erro de texto puro quando o acesso ocorre fora do período permitido [16].
* [x] **Páginas de Bloqueio Visual:** Criado o template `time_locked.html` com Card Bootstrap e cronômetro regressivo inteligente para acessos antecipados [17].
* [x] **Solicitação de Certificado:** Substituído o campo `expires_at` por `certificate_start` e `certificate_end` no modelo `Course` para controle bidirecional (abertura e fechamento) [11].
* [x] **Inscrição Pré-Evento:** Utilização dos campos `registration_start` e `registration_end` para controle de acesso ao formulário de inscrição [11].
* [x] **Travas de Segurança (Backend):** Implementada lógica robusta no método `dispatch` das views para bloquear acesso fora dos períodos definidos, retornando `HttpResponseForbidden` [11].
* [x] **Controle Independente de Links:** Criadas as views `ToggleRegistrationLinkView` e `ToggleCertificateLinkView` para permitir encerrar ou reabrir links de inscrição e certificados de forma isolada via POST [11].
* [x] **Novas Rotas de Controle:** Adicionados endpoints `/toggle-registration/` e `/toggle-certificate/` para gerenciamento fino do status dos eventos [11].
* [x] **Redesign da Listagem (UX):** Coluna de links reformulada com cards individuais, input-groups de cópia e botões de toggle independentes com estados dinâmicos (Encerrar/Reabrir) [11].
* [x] **Interface Administrativa (UX):** `CourseForm` atualizado com cards simétricos para Inscrição e Certificado, incluindo switches (toggles) e lógica JS independente para controle de períodos [11].
* [x] **Integração de Backend (UX):** View `CourseListView` agora injeta `now` no contexto para precisão visual no status dos links [11].

**Gestão de Eventos e Solicitações:**
* [x] CRUD completo de Cursos com suporte a URLs Amigáveis (Slugs) [8].
* [x] **Clean URLs:** Remoção de Query Strings. Links seguem o padrão profissional: `/solic-cert-nome-do-curso-uuid/` e `/inscricao/nome-do-curso-uuid/` [8, 10].
* [x] **Sistema de Expiração de Certificado:** Card dedicado no formulário para controle visual claro sobre a validade do link de emissão [8].
* [x] **Kill-Switch (Blindagem):** Bloqueio automático de acesso ao formulário caso a data de expiração tenha sido atingida [8].
* [x] **Controle de Presença:** Novo campo `attended` no modelo `Registration` para validação futura de emissão [10].

**Correções e Melhorias Técnicas:**
* [x] **Otimização de Lógica:** Implementada propriedade `@property is_expired` no modelo `Course` para centralizar a regra de expiração [8].
* [x] **Formatação ISO em Forms:** Forçada a formatação ISO nos campos de data e hora do `CourseForm` para garantir exibição correta em inputs HTML5 no modo de edição [15].
* [x] **Validação via ViaCEP:** Captura automática de endereço (Rua, Bairro, Cidade, UF) em formulários públicos e administrativos [19, 20].

**Central de Certificados e PDF:**
* [x] Geração profissional com ReportLab (A4 Paisagem) [14, 21].
* [x] Suporte a `CertificateTemplate` (Upload de arte de fundo e textos personalizados) [7].
* [x] QR Code e código numérico de 12 dígitos gerados automaticamente [14, 18].
* [x] View pública de verificação de autenticidade sincronizada com dados de Instituição/Local [7, 17].

**Background Jobs (Celery):**
* [x] Envio de e-mails via SMTP assíncrono isolado da *view* web [17].

---

#### ⏳ O que está pausado / Em Standby
* **Módulo de WhatsApp:** Preparado no `whatsapp_sender.py` para rodar na API WAHA, mas intencionalmente desativado via `.env` (`WAHA_ENABLED = False`) [15, 16].

---

#### 🔴 O que ainda precisa ser feito (Roadmap)
**Prioridade Alta:**
* [ ] **Monetização e Assinaturas:** Desenvolvimento de planos de cobrança (Pacote de Créditos ou Assinatura Mensal). Integração com Gateway de Pagamento.

**Prioridade Média:**
* [ ] Deploy em ambiente de homologação [22].
* [ ] Refatorar envio do WhatsApp para API Oficial da Meta [22].
