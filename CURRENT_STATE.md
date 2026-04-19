# 📊 CURRENT_STATE.md — Estado Atual do Projeto

**Atualize este arquivo após cada sessão de desenvolvimento.** A IA deve ler este arquivo para entender o escopo completo.

#### 🗓️ Última atualização: 2026-04-11 (Refatoração de Regras de Negócio) [15]

---

#### ✅ O que já está implementado [6]
**Estrutura Base e SaaS:**
* [x] Refinamento de UX/Copy: Rodapés de templates, URLs de PDFs de preview e e-mails atualizados para a estratégia PLG (gocertificado.com e app.gocertificado.com).
* [x] Rebranding do sistema para GoCertificado e atualização de URLs e domínios de produção para app.gocertificado.com
* [x] Arquitetura SaaS Multitenant (Login, Registro e Perfil vinculados a Empresas) [6, 11].
* [x] Models: `Company`, `Instructor`, `Course`, `Registration`, `Certificate`, `CertificateTemplate` [11, 17, 18].
* [x] **Refatoração de UX Copy:** Nomenclatura alterada de "Treinamento" para "Evento" em todo o painel administrativo, modelos e templates [9, 10].
* [x] **Padronização de Nomenclatura:** Termos de "Inscrição" alterados para "Solicitação de Certificado" em formulários de emissão [8].

**Correções e Refinamentos (Recente):**
* [x] **Motor de Regras de Certificado:** Implementadas as 6 regras de negócio no backend para gerenciar o fluxo de inscription e solicitação de certificado, com mensagens personalizadas enviadas via sessão. [48]
* [x] **Refinamento de UX (Inscrição):** Refatorada a lógica condicional de exibição de datas no cabeçalho dos formulários de inscrição (Padrão e Customizado). O sistema agora padroniza a mensagem "Link de inscrição vitalício" para eventos sem prazo definido e organiza elegantemente os horários de início e encerramento. [NOVO]
* [x] **Tabela de Impressão (Bugfix):** Refatoração agressiva do CSS `@media print` para garantir o alinhamento perfeito de bordas e linhas na Lista de Presença em formato A4 [15].
* [x] **Layout de Impressão (UX):** O layout de impressão da Lista de Presença foi otimizado para formato Paisagem (Landscape) e implementada a classe `nowrap-print` para evitar quebras de linha nas colunas de identificação [16].
* [x] **Refinamento de Impressão (UX):** Layout de impressão da Lista de Presença refinado com a inclusão do campo Profissão ao lado do CPF e ajustes estruturais no campo de Assinatura (alinhamento e estilo de linha) [17].
* [x] **Bugfix de Layout de Impressão:** Corrigido o erro de bordas duplicadas e títulos cortados na tabela de impressão através do ajuste de `display: table-cell` para elementos exclusivos de impressão [18].
* [x] **Match de CPF e Automação (UX/Backend):** Implementada lógica de "Match de CPF" que permite ao aluno atualizar seus dados durante a solicitação de certificado. Adicionado disparo automático da `issue_certificate_task` via Celery para alunos com presença confirmada (`attended=True`) [19].
* [x] **Controle de Períodos (SaaS):** Refatorada a modelagem do Evento para substituir o campo único `expires_at` por um controle bidirecional de emissão (`certificate_start` e `certificate_end`), permitindo agendar a abertura e o fechamento das solicitações de certificado de forma independente. O template `course_form.html` foi atualizado para suportar a injeção destes campos via DOM com validação dinâmica. [NOVO]

* [x] **Autofill Inteligente (UX):** Implementado motor de preenchimento automático no `CourseForm` que sugere datas e horários coerentes (hoje e amanhã) para novos eventos, agilizando o processo de cadastro para o administrador. [NOVO]
* [x] **Proteção de Duplicidade (Inscrição):** Reforçada a validação em `EventRegistrationCreateView` para impedir inscrições duplicadas de um mesmo CPF no mesmo evento. O sistema agora desacopla a mensagem de erro contextual em uma flag `duplicate_error`, disparando automaticamente um Modal de Interrupção reativo no frontend (templates Padrão e Customizado). [17/04/2026]
* [x] **Ajuste de Diagramação (ReportLab):** O espaçamento vertical do Modelo de Certificado Padrão foi ajustado para melhorar a diagramação, aproximando o título da logomarca e distribuindo melhor os blocos de texto no eixo Y.
* [x] **Correções e Melhorias Técnicas:** As coordenadas e espaçamentos do Modelo Personalizado (ReportLab) foram ajustados (y=400 para título, redução de gap pós-t1 para 0.7cm e ancoragem y=375 para corpo) para garantir a exibição correta das assinaturas no rodapé e aproximar o bloco 'Certificamos que' do título.
* [x] **Refatoração de View (SaaS):** A View `CertificateDesignView` foi refatorada para manter a persistência do formulário (`instance`) e isolar o salvamento da Logomarca, garantindo integridade dos dados durante as configurações de design.
* [x] **CRUD de Modelos de Certificado:** Implementado o CRUD completo para `CertificateTemplate`, permitindo a criação, edição e exclusão de modelos personalizados com persistência de estado e seleção dinâmica na interface de design.
* [x] **Correções e Melhorias Técnicas:** O código legado de `certificate_model` global foi removido de `forms.py` e `views.py` para consolidar a arquitetura por Evento, eliminando redundâncias e centralizando a escolha do layout no curso.
* [x] **Refatoração de UI (Design):** A interface de Configuração de Certificados foi refatorada para um Gerenciador de Ativos limpo, removendo lógicas de toggle obsoletas e consolidando o Construtor de Modelos Personalizados como uma ferramenta independente.
* [x] **Magic Link de Credenciamento:** Criada a infraestrutura de backend (Hash UUID, Views e Rotas) e a interface dedicada (`public_checkin.html`) para o Magic Link de credenciamento público e check-in em massa, permitindo o controle de presença externo seguro com opções de cópia e revogação de acesso no painel administrativo.
* [x] **Bugfix de Rota:** Corrigido o erro `NoReverseMatch` na rota `public_toggle_presence` ajustando a tipagem para UUID e removendo argumentos redundantes no template `public_checkin.html`.
* [x] **Refatoração de Rotas (SaaS):** As rotas de credenciamento público foram movidas para o aplicativo raiz (`registrations`), garantindo URLs limpas e removendo a dependência de autenticação de sessão para o acesso via Magic Link. Implementado também o endpoint de check-in individual público e realizados os ajustes de namespace nos templates `presence_list.html` e `public_checkin.html`.
* [x] **Melhorias Técnicas (Credenciamento):** A View `PublicTogglePresenceView` agora dispara a task do Celery `issue_certificate_task` automaticamente ao confirmar a presença do aluno, garantindo a emissão imediata para solicitações pendentes.
* [x] **Bugfix de Template:** Corrigido o erro de `TemplateDoesNotExist` na `PublicCheckinView` ajustando o `template_name` para o caminho correto (`core/public_checkin.html`).
* [x] **Segurança e Compatibilidade (Credenciamento):** As Views públicas de Credenciamento receberam a importação de `JsonResponse` e a isenção `@method_decorator(csrf_exempt, name='dispatch')` para evitar bloqueios de CSRF em abas anônimas e dispositivos móveis, garantindo o funcionamento do Magic Link na porta do evento.
* [x] **Quick Link Email API:** Criado endpoint na API pública de credenciamento (`PublicSendLinkEmailView`) para envio rápido de links de inscrição e certificado via e-mail utilizando o SMTP do sistema.
* [x] **Refatoração de UI/UX (Credenciamento):** O painel de credenciamento público foi refatorado para exibir cards de "Links de Acesso Rápido" (Inscrição e Certificado). A tabela de participantes agora conta com numeração sequencial (#), exibição de profissão e um motor de feedback visual imediato (badge interativo) no Check-in individual via AJAX.
* [x] **Impressão Multimodal:** Implementada funcionalidade de impressão com dois modos (Física e Digital) no painel de credenciamento público. A Imressão Digital foi corrigida com fallback de texto limpo para o Status, garantindo legibilidade perfeita em PDFs.
* [x] **Correções e Melhorias Técnicas:** O método `save()` do modelo `Course` foi refatorada para injetar o `checkin_hash` automaticamente, evitando erros de migração com callable defaults em tabelas populadas.
* [x] Sprint 3 Concluída: Finalizada a implementação da Automação Celery baseada em Match de CPF e Check-in, incluindo atualização de UX na tela de sucesso para feedback em tempo real [20].
* [x] Modelagem de dados do NPS (NPSForm, NPSQuestion, NPSResponse) e vínculo com modelo Course adicionados.
* [x] **Higienização de Template:** O arquivo `templates/registrations/form.html` foi sanitizado para remover duplicação de código e tags de bloco redundantes (`{% block ... %}`), consolidando-o como uma página standalone válida. [54]
* [x] **Higienização Definitiva (Admin):** Removidas duplicidades de campos e blocos HTML de NPS no `CourseForm` e `course_form.html` que causavam instabilidade no salvamento de eventos. [56]
* [x] **Bugfix de Transição (Bootstrap):** Corrigida a "Race Condition" no `form.html` utilizando o listener `hidden.bs.modal` para garantir que o modal de confirmação feche completamente antes da abertura do modal NPS. [57]
* [x] **Bypass Técnico NPS (Frontend):** Refatorada a validação do `form.html` para realizar bypass temporário do atributo `required` dos campos NPS durante a submissão do formulário principal, resolvendo conflitos de validação nativa. [58]
* [x] **Robustez NPS (Backend):** Implementada blindagem anti-forging no processamento de respostas NPS, capturando `NPSQuestion.DoesNotExist` para evitar erros 500 em requisições malformadas ou forjadas. [59]
* [x] **Correção Estrutural:** O campo `nps_form` no modelo `Course` foi reposicionado para logo abaixo de `certificate_template` e seus parâmetros foram atualizados para garantir a integração correta com a pesquisa de satisfação. [53]
* [x] Backend CRUD do NPS (Forms, Views, URLs) construído e protegido via Multitenant.
* [x] Etapa 3 do NPS: Interfaces administrativas de criação e edição de formulários e injeção do seletor no cadastro de Eventos.
* [x] Etapa 4 do NPS: Interceptação via Modal Frontend no fluxo público de solicitação de certificados e persistência inteligente de respostas (NPSResponse) no Backend.
* [x] Refinamento de UX de Sucesso (Sprint 3): Injetados dados do evento (`course_name`, `course_date`) na sessão e refatorada a tela de sucesso para exibir mensagens dinâmicas e personalizadas, confirmando a geração automática de certificados para alunos com check-in [21].
* [x] **Bugfix de Falso Positivo (Celery):** O bug de falso positivo de sucesso no envio de certificado foi corrigido, atrelando a mudança de status da inscrição apenas ao sucesso real do SMTP ou WhatsApp (WAHA) [21].
* [x] **Trava de Re-emissão (UX/Backend):** Implementada trava de segurança que impede a re-emissão de certificados já enviados (`status=SENT`), redirecionando o aluno para a tela de sucesso com uma flag específica (`already_requested`) [22].
* [x] **Refinamento de UX de Sucesso (Copy Final):** Refatoração completa da tela de sucesso com o copy exato solicitado pelo cliente, incluindo o tratamento visual para duplicidade e automação de envio [23].
* [x] **Padronização Visual (Páginas de Sucesso):** Refatorada a página de sucesso para renderizar dinamicamente a mensagem construída pelo motor de regras do backend, utilizando um design limpo com ícone de envelope e botão de fechamento de janela. [49]
* [x] **Refinamento de Copy (Solicitação Pendente):** O texto da mensagem de sucesso para solicitações que aguardam check-in foi refinado, adicionando orientações explícitas sobre a verificação de SPAM e lixo eletrônico [27].
* [x] **Design de Gaveta (Listagem):** O Accordion da listagem de eventos foi encapsulado em um design de "Card/Gaveta" com header interno e borda âncora azul marinho, resolvendo a poluição visual em aberturas simultâneas e melhorando a identificação do evento nos controles [43].
* [x] **Refinamento de UI (Listagem):** O botão de "Lista de Presença" (Check-in) na listagem de cursos foi atualizado para um layout robusto de ícone sólido marinho com legenda inferior, integrando-se harmonicamente à nova linha expansível de controles [42].
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
* [x] **UX de Erro Temporal:** Refatoração do backend (`dispatch`) para renderizar template elegante (`time_locked.html`) ou (`revoked_link.html`) em vez de erro de texto puro quando o acesso ocorre fora do período permitido ou o link foi revogado. A View `PublicCheckinView` agora intercepta `Course.DoesNotExist` e renderiza a tela de acesso revogado com status 404.
* [x] **Páginas de Bloqueio Visual:** Criado o template `time_locked.html` com Card Bootstrap e cronômetro regressivo inteligente para acessos antecipados, e o template `revoked_link.html` para acessos a links desativados pelo administrador.
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

* [x] **Módulo de Credenciamento Público (Portaria):**
* [x] Criação de tela pública isolada para credenciamento protegida por Hash UUID.
* [x] Ações em massa para check-in/check-out e disparo rápido de e-mail (SMTP) na porta do evento.
* [x] **Check-in em Massa (Admin):** Implementada a lógica Javascript para Check-in em Massa e impressão multimodal (Digital/Física) no painel administrativo, sincronizada com o motor de badges e horários em tempo real.
* [x] **Espelhamento de Layout (Admin):** O painel administrativo da Lista de Presença foi atualizado para espelhar o layout da tabela pública, incluindo a barra de ações em massa, contador dinâmico, exibição de data/hora de check-in e o campo Profissão do participante (presence_list.html).
* [x] **Fuso Horário (Accreditation):** O fuso horário (timezone) foi fixado nas respostas AJAX das Views de credenciamento (individual e em massa) utilizando `localtime()`, garantindo que o horário exibido no frontend respeite a configuração local.
* [x] **Refinamento de UI (Dashboard Público):** Refinada a interface dos botões de impressão (correção de hover), implementada a exibição dinâmica da data/hora do check-in na tabela e atualizado o motor Javascript para sincronização em tempo real desses dados.
* [x] **Persistência de Check-in:** As Views de credenciamento (individual e em massa) agora gravam a data/hora exata do check-in no banco de dados e retornam essa informação formatada para o frontend.
* [x] **UI Limpa:** Removida a coluna redundante "Sel" (checkbox individual inativo) da tabela de credenciamento público para eliminar conflitos visuais com a chave de Status.
* [x] **Master Checkbox:** Implementada UI de Master Checkbox com suporte a status `indeterminate`, contador dinâmico sincronizado e disparo de requisição AJAX para processamento em massa. A UI foi refinada com foco em UX (Microcopy: Check-in em Massa) e design destacado.
* [x] Feedback visual dinâmico (Badge e Switch) com persistência imediata via AJAX (1-Click Check-in).
* [x] **Auto-Emissão Assíncrona:** Disparo automático da fila Celery vinculada à confirmação de presença do participante (individual e em massa).
* [x] Impressão Multimodal com regras CSS Print: Lista física (com linha de assinatura) e digital (status em texto limpo).

**Correções e Melhorias Técnicas:**
* [x] **Trava Anti-Certificado (UX):** Implementado um Toggle Switch chamativo ("ESTE EVENTO NÃO TERÁ CERTIFICADO") no formulário de curso. A ativação desta flag oculta dinamicamente via JavaScript todas as configurações de emissão e design, otimizando o fluxo para eventos informativos ou reuniões.
* [x] **Gestão de Emissão:** Adicionado o campo `no_certificate` ao modelo `Course` e `CourseForm`, permitindo desativar a emissão de certificados para eventos específicos.
* [x] **UX de Edição de Participante:** A tela de edição de participante (`participant_form.html`) recebeu lógica JavaScript para ocultação dinâmica condicional do campo de Gênero Personalizado, aprimorando a UX e garantindo a limpeza de dados não utilizados.
* [x] **Refinamento de RegistrationForm:** O widget `DateInput` do campo `birth_date` recebeu o parâmetro `format='%Y-%m-%d'` para garantir a renderização correta em inputs HTML5 no painel de edição. As labels dos campos `gender` e `custom_gender` foram refinadas para maior clareza.
* [x] **Edição de Participantes:** Implementada a funcionalidade de edição de dados dos participantes no backend (UpdateView) com proteção Multitenant rigorosa, criado o template frontend correspondente (`participant_form.html`) e o botão "Editar Cadastro" foi movido para o cabeçalho principal do acordeão de participantes. Foi aplicada a técnica de Zebra Striping (`{% cycle ... silent %}`) nos itens da lista com contraste aprimorado (`bg-secondary bg-opacity-10`) e a técnica de Shrink-to-fit nas colunas de ação para otimizar o espaço.
* [x] **UX de Erros Críticos:** A interface do formulário de solicitação (`form.html`) recebeu um Modal Extravagante (Bootstrap 5) para interrupção de fluxo em caso de bloqueio de segurança (Spoofing) ou CPF inexistente.
* [x] **Acessibilidade (Zebra Striping):** O contraste da cor do Zebra Striping foi ajustado (de `#f9f9f9` para `#dce4ec`) para tornar a alternância de linhas mais evidente e melhorar a acessibilidade visual na listagem de eventos [45].
* [x] **Zebra Striping (Listagem):** O Zebra Striping na listagem de eventos foi resolvido de forma definitiva manipulando a variável `--bs-table-bg` inline via `forloop` do Django, garantindo compatibilidade total com o Bootstrap 5 e legibilidade superior [44].
* [x] **Interface Mestre-Detalhe:** A interface de listagem de cursos foi refatorada com o padrão Mestre-Detalhe (Accordion Rows) para ocultar e organizar os links e controles de forma limpa [39].
* [x] **Emissão Automática via Check-in:** A emissão de certificados agora é disparada automaticamente (via Celery) ao habilitar a chave de Check-in na Lista de Presença, caso o aluno já possua uma solicitação com status Pendente [38].
* [x] **Otimização de Lógica:** Implementada propriedade `@property is_expired` no modelo `Course` para centralizar a regra de expiração [8].
* [x] **Ajuste de Fluxo (Duplicidade):** O fluxo de duplicidade no backend foi refatorado para respeitar reversões de check-in e disparar o Celery corretamente, e o copy visual da tela de pendência foi ajustado para maior clareza [31].
* [x] **Máquina de Estados (Database Tracking):** Refatorada a lógica do `form_valid` para integrar o campo persistente `certificate_requested`. O sistema agora diferencia com precisão milimétrica as 4 condições de sucesso (Inédita, Duplicidade Pendente, Já Enviado e Automação) utilizando uma combination de estado de banco e flags de sessão [36].
* [x] **Segurança Anti-Fraude:** Implementada trava de segurança na View de solicitação de certificado que impede o roubo de identidade e a sobrescrita de dados sensíveis (Nome, CPF, RG, Data de Nascimento). O sistema agora valida o nome informado contra o nome cadastrado na inscrição (com normalização de strings) e blinda os campos core da identidade.
* [x] **Bugfix de Extração de Nome:** Corrigido o bug de extração do primeiro nome nas Views de inscription e solicitação, garantindo a exibição correta como string simples em vez de lista.
* [x] **Correções e Melhorias Técnicas:** O método `get_registration_url` do modelo `Course` foi corrigido para retornar a rota `registrations:event_form`, consertando o bug do envio de link incorreto por e-mail na página de credenciamento.
* [x] **Correções e Melhorias Técnicas:** Corrigido o bug de redirecionamento NoneType nas views de formulário público (Inscrição e Solicitação) atribuindo corretamente a propriedade self.object antes do redirecionamento de sucesso. [52]
* [x] **Melhorias Técnicas (UX):** A UI da tela de Sucesso (`registration_success.html`) foi aprimorada com layout moderno (ícone de foguete) e recebeu um fallback de JavaScript para lidar com o bloqueio de `window.close()` imposto pelos navegadores modernos.
* [x] **Correções e Melhorias Técnicas:** O método `get_context_data` foi restaurado nas Views de inscrição/solicitação para corrigir a exibição dinâmica dos dados do evento (Nome, Data, Carga Horária, Local) no frontend. [50]
* [x] **Controle de Estado de Solicitação:** Adicionada a flag `is_requested` ao modelo `Registration` para diferenciar com precisão a inscrição pré-evento da solicitação de certificado pós-evento. O disparo da emissão automática via check-in (individual ou em massa) agora exige que esta flag seja `True`. [46, 47]
* [x] **Formatação ISO em Forms:** Forçada a formatação ISO nos campos de data e hora do `CourseForm` para garantir exibição correta em inputs HTML5 no modo de edição [15, 55].
* [x] **Persistência de Solicitação (Database):** Adicionado o campo booleano `certificate_requested` e o campo de data/hora `checkin_at` ao modelo `Registration` para rastrear de forma persistente se o aluno já realizou a solicitação do certificado e o momento exato do check-in.
* [x] **Formatação ISO em Forms:** Forçada a formatação ISO nos campos de data e hora do `CourseForm` para garantir exibição correta em inputs HTML5 no modo de edição [15].
* [x] **Segurança e UX (Páginas de Bloqueio):** O arquivo `time_locked.html` foi criado fisicamente na raiz de `templates/` para suportar as views de interrupção visual (acesso antecipado ou encerrado) com cronômetro regressivo.
* [x] **Segurança e UX (Páginas Públicas):** As views `RegistrationCreateView` (Solicitação de Certificado) e `EventRegistrationCreateView` (Inscrição em Evento) foram refatoradas para utilizar o template de interrupção visual com cronômetro (`time_locked.html`) em vez de respostas HTTP HTML estáticas para bloqueios de período. Corrigida a renderização condicional de datas no cabeçalho (UX), padronizando a exibição para cenários de links vitalícios.
* [x] **Segurança e UX (Credenciamento):** Implementada blindagem da flag `no_certificate` na tela pública de credenciamento (`public_checkin.html`), ocultando o link de solicitação e exibindo um alerta visual informativo quando o evento não gera certificado.
* [x] **Segurança e UX (Formulário de Evento):** A lógica de validação JS em `course_form.html` recebeu um bypass para ignorar o modal de falta de assinatura e o aviso de expiração quando a flag de "Evento Sem Certificado" estiver ativa.
* [x] **Validação via ViaCEP:** Captura automática de endereço (Rua, Bairro, Cidade, UF) em formulários públicos e administrativos. Adicionado link de busca oficial dos Correios e motor JS ViaCEP customizado no `event_form.html`. [19, 20, 51]
* [x] **Arquitetura de Formulários Dinâmicos (EAV):** Construída a base de dados para suporte a formulários dinâmicos personalizados. Implementados os modelos `DynamicForm`, `DynamicField` (Atributos) e `DynamicResponse` (Valores), e vinculados ao modelo `Course` para customização de fluxos de Inscrição e Solicitação. [17/04/2026]
* [x] **CRUD de Formulários Dinâmicos:** Implementadas Views (CBVs), Forms (Inline Formsets) e Templates para gerenciamento de formulários dinâmicos. Adicionado suporte a manipulação de campos via Vanilla JS no frontend com re-indexação automática de prefixos do Django. Proteção Multitenant aplicada em todas as camadas. [17/04/2026]
* [x] **Tipagem de Contexto EAV:** Adicionado o campo `form_type` ao modelo `DynamicForm`, permitindo distinguir e filtrar formulários de "Inscrição" e "Solicitação de Certificado" visualmente e logicamente. [17/04/2026]
* [x] **Arquitetura EAV Flexível:** O modelo `Registration` foi ajustado para permitir campos opcionais (`birth_date`, `whatsapp`, `rg`), permitindo que empresas configurem formulários mínimos ou complexos via sistema EAV. [17/04/2026]
* [x] **Desacoplamento e Roteamento EAV:** Implementado motor de roteamento de templates e desacoplamento de obrigatoriedade no backend. O sistema agora seleciona automaticamente entre templates padrão e customizados (`_custom.html`) e ajusta a validação do formulário em tempo de execução baseado no contexto do Evento. [NOVO]
* [x] **Conexão EAV-Evento:** Conectada a injeção restrita de formulários dinâmicos à interface de criação de eventos. Os seletores agora filtram automaticamente formulários por contexto (REG vs CERT) e garantem o isolamento multitenancy, permitindo o uso opcional do modelo padrão ou personalizado. [17/04/2026]
* [x] **Integração EAV (Público):** Formulários dinâmicos integrados aos fluxos de Inscrição Pré-Evento e Solicitação de Certificado. Implementada técnica de EAV Injection via contexto para renderização dinâmica de campos (text, email, number, date, select e checkbox) e recuperação iterativa via POST para persistência em `DynamicResponse`. [17/04/2026]

* [x] **Trava de Identidade Core (UX/EAV):** Implementada barreira visual no Form Builder do EAV, fixando Nome, CPF, E-mail e Data de Nascimento como campos obrigatórios inalteráveis (posições 1 a 4). Adicionado motor Javascript para recálculo automático de ordem (`index + 5`) em campos dinâmicos, garantindo a integridade da Identidade Core e blindagem visual completa no motor do construtor. [NOVO]
* [x] **Obrigatoriedade Estrita (Formulário Padrão):** Implementada obrigatoriedade total para todos os campos de dados pessoais e endereço (`gender`, `profession`, `whatsapp`, `rg`, `cep`, `street`, `number`, `neighborhood`, `city`, `state`) nos fluxos padrão de Inscrição e Certificado. Esta mudança garante a integridade máxima do banco de dados enquanto preserva o isolamento flexível do motor EAV para formulários customizados. [NOVO]
* [x] **Segurança Anti-Spoofing (2FA):** A Data de Nascimento foi elevada a pilar obrigatório e fator de validação de identidade. O sistema agora bloqueia solicitações se a data informada não coincidir com o cadastro original. O campo 'e-mail' foi liberado para atualizações pelos alunos, permitindo a correção de falhas de comunicação. [17/04/2026]
* [x] **Blindagem de Validação EAV:** Refatorados os métodos `clean_cpf` e `clean_whatsapp` no `RegistrationForm` para tratar valores nulos ou vazios. Esta blindagem impede erros de execução (TypeError) quando estes campos não são obrigatórios em formulários EAV customizados. [NOVO]




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
**Prioridade Prioridade Baixa:**
* [ ] **Monetização e Assinaturas:** Desenvolvimento de planos de cobrança (Pacote de Créditos ou Assinatura Mensal). Integração com Gateway de Pagamento.

**Prioridade Baixa:**
* [ ] Deploy em ambiente de homologação [22].
* [ ] Refatorar envio do WhatsApp para API Oficial da Meta [22].
