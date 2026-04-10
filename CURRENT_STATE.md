# 📊 CURRENT_STATE.md — Estado Atual do Projeto

**Atualize este arquivo após cada sessão de desenvolvimento.** A IA deve ler este arquivo para entender o escopo completo.

#### 🗓️ Última atualização: 2026-04-10 (Controle de Período de Solicitação e Inscrição) [11]

---

#### ✅ O que já está implementado [6]
**Estrutura Base e SaaS:**
* [x] Arquitetura SaaS Multitenant (Login, Registro e Perfil vinculados a Empresas) [6, 11].
* [x] Models: `Company`, `Instructor`, `Course`, `Registration`, `Certificate`, `CertificateTemplate` [11, 17, 18].
* [x] **Refatoração de UX Copy:** Nomenclatura alterada de "Treinamento" para "Evento" em todo o painel administrativo, modelos e templates [9, 10].
* [x] **Padronização de Nomenclatura:** Termos de "Inscrição" alterados para "Solicitação de Certificado" em formulários de emissão [8].

**Sistema de Controle de Períodos e UX Reativa (Novo):**
* [x] **Cronômetro Reativo:** Implementada lógica Vanilla JS com `setInterval` para contagem regressiva em tempo real nos formulários de Inscrição e Solicitação de Certificado [12].
* [x] **Exibição Explícita de Datas:** Adicionado card `alert-info` no topo dos formulários públicos exibindo datas de início e encerramento formatadas (Django `|date`) [12].
* [x] **Bloqueio Visual Dinâmico:** Ocultação automática do formulário (`display: none`) e exibição de status "Abre em", "Expira em" ou "Encerrado" baseada no horário do cliente sincronizado com o servidor [12].
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
