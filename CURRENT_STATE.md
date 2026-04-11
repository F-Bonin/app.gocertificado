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
* [x] **Match de CPF e Automação (UX/Backend):** Implementada lógica de "Match de CPF" que permite ao aluno atualizar seus dados durante a solicitação de certificado. Adicionado disparo automático da `issue_certificate_task` via Celery para alunos com presença confirmada (`attended=True`) [19].
* [x] **Proteção de Duplicidade (Inscrição):** Reforçada a validação em `EventRegistrationCreateView` para impedir inscrições duplicadas de um mesmo CPF no mesmo evento [19].
* [x] **Sprint 3 Concluída:** Finalizada a implementação da Automação Celery baseada em Match de CPF e Check-in, incluindo atualização de UX na tela de sucesso para feedback em tempo real [20].
* [x] **Refinamento de UX de Sucesso (Sprint 3):** Injetados dados do evento (`course_name`, `course_date`) na sessão e refatorada a tela de sucesso para exibir mensagens dinâmicas e personalizadas, confirmando a geração automática de certificados para alunos com check-in [21].
* [x] **Bugfix de Falso Positivo (Celery):** O bug de falso positivo de sucesso no envio de certificado foi corrigido, atrelando a mudança de status da inscrição apenas ao sucesso real do SMTP ou WhatsApp (WAHA) [21].
* [x] **Trava de Re-emissão (UX/Backend):** Implementada trava de segurança que impede a re-emissão de certificados já enviados (`status=SENT`), redirecionando o aluno para a tela de sucesso com uma flag específica (`already_requested`) [22].
* [x] **Refinamento de UX de Sucesso (Copy Final):** Refatoração completa da tela de sucesso com o copy exato solicitado pelo cliente, incluindo o tratamento visual para duplicidade e automação de envio [23].
* [x] **Padronização Visual (Páginas de Sucesso):** Padronizado o design de todos os fluxos de sucesso (Inscrição, Solicitação, Automação e Duplicidade) com ícones grandes, títulos semânticos e estrutura visual consistente [26].
* [x] **Refinamento de Copy (Solicitação Pendente):** O texto da mensagem de sucesso para solicitações que aguardam check-in foi refinado, adicionando orientações explícitas sobre a verificação de SPAM e lixo eletrônico [27].
* [x] **Design de Gaveta (Listagem):** O Accordion da listagem de eventos foi encapsulado em um design de "Card/Gaveta" com header interno e borda âncora azul marinho, resolvendo a poluição visual em aberturas simultâneas e melhorando a identificação do evento nos controles [43].
* [x] **Refinamento de UI (Listagem):** O botão de "Lista de Presença" (Check-in) na listagem de cursos foi atualizado para um layout robusto de ícone sólido marinho com legenda inferior, integrando-se harmonicamente à nova linha expansível de controles [42].
* [x] **Polimento de UI (Páginas de Sucesso):** O layout das páginas de sucesso foi polido com a remoção de títulos duplicados herdados da versão antiga, garantindo uma interface mais limpa e focada nas mensagens específicas [24].
* [x] **Segurança e UX Preventiva:** Implementado Modal Bootstrap de confirmação de dados (Nome/CPF) com bloqueio de duplo-clique no botão de envio para evitar disparos simultâneos (*Race Condition*) e fornecer feedback visual de processamento [37].
* [x] **Trava de Duplicidade:** Reforçada a lógica de backend para impedir re-emissão de certificados já enviados, economizando recursos de processamento [24].
* [x] **Bugfix de Redirecionamento (Trava de Duplicidade):** Corrigido o erro `'NoneType' object has no attribute 'dict'` ao interceptar solicitações duplicadas, garantindo a injeção do `self.object` antes da chamada de `get_success_url()` [25].
* [x] **Barreira de Reenvio (Pendentes):** Implementada a flag `already_pending` na sessão para identificar e barrar visualmente o reenvio de formulários de alunos que já solicitaram o certificado e aguardam o check-in [28].
* [x] **Refinamento de UX de Sucesso (Copy Final):** O copy da tela de pendência foi ajustado para maior clareza e uma nova tela de bloqueio visual para Duplicidades Pendentes (`already_pending`) foi implementada para evitar confusão do usuário [29].
* [x] **Automação de Reenvio (Pendentes):** Refatorada a lógica do `form_valid` para permitir que alunos com status `PENDING` acionem a `issue_certificate_task` via Celery caso o check-in seja detectado durante uma nova submissão do formulário [30].
* [x] **Refatoração de Sessão e UX:** Refatorado o método `form_valid` para garantir a extração e persistência do primeiro nome do aluno na sessão em todos os fluxos, e padronizado o resgate centralizado de flags na `RegistrationSuccessView` para um feedback visual mais preciso e personalizado [32].
* [x] **Condições de Sucesso (Copy Final):** Aplicadas as 4 condições de sucesso exatas estipuladas pelo cliente no template `registration_success.html`, garantindo a ordem lógica e o copy integral para automação, duplicidades e solicitações pendentes [33].

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
* [x] **Acessibilidade (Zebra Striping):** O contraste da cor do Zebra Striping foi ajustado (de `#f9f9f9` para `#dce4ec`) para tornar a alternância de linhas mais evidente e melhorar a acessibilidade visual na listagem de eventos [45].
* [x] **Zebra Striping (Listagem):** O Zebra Striping na listagem de eventos foi resolvido de forma definitiva manipulando a variável `--bs-table-bg` inline via `forloop` do Django, garantindo compatibilidade total com o Bootstrap 5 e legibilidade superior [44].
* [x] **Interface Mestre-Detalhe:** A interface de listagem de cursos foi refatorada com o padrão Mestre-Detalhe (Accordion Rows) para ocultar e organizar os links e controles de forma limpa [39].
* [x] **Emissão Automática via Check-in:** A emissão de certificados agora é disparada automaticamente (via Celery) ao habilitar a chave de Check-in na Lista de Presença, caso o aluno já possua uma solicitação com status Pendente [38].
* [x] **Otimização de Lógica:** Implementada propriedade `@property is_expired` no modelo `Course` para centralizar a regra de expiração [8].
* [x] **Ajuste de Fluxo (Duplicidade):** O fluxo de duplicidade no backend foi refatorado para respeitar reversões de check-in e disparar o Celery corretamente, e o copy visual da tela de pendência foi ajustado para maior clareza [31].
* [x] **Máquina de Estados (Database Tracking):** Refatorada a lógica do `form_valid` para integrar o campo persistente `certificate_requested`. O sistema agora diferencia com precisão milimétrica as 4 condições de sucesso (Inédita, Duplicidade Pendente, Já Enviado e Automação) utilizando uma combinação de estado de banco e flags de sessão [36].
* [x] **Persistência de Solicitação (Database):** Adicionado o campo booleano `certificate_requested` ao modelo `Registration` para rastrear de forma persistente se o aluno já realizou a solicitação do certificado através do formulário público [35].
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
