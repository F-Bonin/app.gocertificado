# 📊 CURRENT_STATE.md — Estado Atual do Projeto

**Atualize este arquivo após cada sessão de desenvolvimento.** A IA deve ler este arquivo para entender o escopo completo.

#### 🗓️ Última atualização: 2026-04-09 (Refatoração de UX Copy: Treinamento para Evento) [9]

---

#### ✅ O que já está implementado [6]
**Estrutura Base e SaaS:**
* [x] Arquitetura SaaS Multitenant (Login, Registro e Perfil vinculados a Empresas) [6, 11].
* [x] Models: `Company`, `Instructor`, `Course`, `Registration`, `Certificate`, `CertificateTemplate` [11, 17, 18].
* [x] **Refatoração de UX Copy:** Nomenclatura alterada de "Treinamento" para "Evento" em todo o painel administrativo e modelos de certificado [9].
* [x] **Padronização de Nomenclatura:** Termos de "Inscrição" alterados para "Solicitação de Certificado" em formulários, modelos e visualização [8].

**Gestão de Treinamentos e Solicitações:**
* [x] CRUD completo de Cursos com suporte a URLs Amigáveis (Slugs) [8].
* [x] **Clean URLs:** Remoção de Query Strings. Links de solicitação agora seguem o padrão profissional: `/solic-cert-nome-do-curso-uuid/` [8].
* [x] **Sistema de Expiração Profissional:** Interface refatorada com Card dedicado no formulário de treinamento, permitindo controle visual claro sobre a validade do link [8].
* [x] **Kill-Switch (Blindagem):** Bloqueio automático de acesso ao formulário caso a data de expiração tenha sido atingida [8].
* [x] **Ação Rápida na Listagem:** Botão "Encerrar/Reabrir" solicitações diretamente no painel, manipulando o status de expiração em tempo real [8].
* [x] Formulário público com captura via ViaCEP (Rua, Número, Bairro, CEP) e dados da Instituição [19, 20].

**Correções e Melhorias Técnicas:**
* [x] **Resolução de Bug (Bugfix):** Corrigido `TemplateSyntaxError` causado por tag de timezone incorreta na listagem de treinamentos [8].
* [x] **Otimização de Lógica:** Implementada propriedade `@property is_expired` no modelo `Course` para centralizar a regra de expiração e limpar o código dos templates [8].

**Central de Certificados e PDF:**
* [x] Geração profissional com ReportLab (A4 Paisagem) [14, 21].
* [x] Suporte a `CertificateTemplate` (Upload de arte de fundo e Título opcional) [7].
* [x] QR Code e código numérico (12 dígitos) gerados automaticamente [14, 18].
* [x] Interface AJAX (Fetch) para emissão em massa e atualização de status em tempo real (Polling) [7, 17].
* [x] View pública de verificação de autenticidade sincronizada com dados de Instituição/Local [7, 17].

**Background Jobs (Celery):**
* [x] Envio de e-mails via SMTP assíncrono isolado da *view* web [17].
* [x] Correção do Reply-To Multi-Tenant dinâmico extraído de `Registration -> Course -> Company` [7].

---

#### ⏳ O que está pausado / Em Standby
* **Módulo de WhatsApp:** Preparado no `whatsapp_sender.py` para rodar na API WAHA, mas intencionalmente desativado via `.env` (`WAHA_ENABLED = False`) aguardando definição de negócios [15, 16].

---

#### 🔴 O que ainda precisa ser feito (Roadmap)
**Prioridade Alta:**
* [ ] **Monetização e Assinaturas:** Desenvolvimento de planos de cobrança (Pacote de Créditos ou Assinatura Mensal) para Escolas e Professores. Integração com Gateway de Pagamento.

**Prioridade Média:**
* [ ] Deploy em ambiente de homologação [22].
* [ ] Refatorar envio do WhatsApp para API Oficial da Meta (caso a empresa opte por não usar o WAHA) [22].
