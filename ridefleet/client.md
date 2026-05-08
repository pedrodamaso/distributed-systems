# 📅 Cronograma — Aplicação Cliente RideFleet
### SIN 142 — Sistemas Distribuídos — UFV 2026/1
> **Período:** 08/05/2026 a 19/06/2026  
> **Para:** Grupos de implementação (serviços clientes conectados ao Core)

---

## O que é responsabilidade do grupo cliente?

| Responsabilidade | Quem implementa |
|-----------------|-----------------|
| Locks, Saga, Circuit Breaker, Consenso, Relógios Lógicos | **Core** |
| Expor e consumir a API padronizada do Core | **Grupo cliente** |
| Back-end do serviço de transporte (corridas, motoristas, passageiros) | **Grupo cliente** |
| Lógica de delegação para outros grupos via API do Core | **Grupo cliente** |
| Front-end (web ou mobile) | **Grupo cliente** |
| Pipeline CI/CD do próprio serviço | **Grupo cliente** |
| Métricas expostas para o Prometheus (endpoint padronizado) | **Grupo cliente** |
| **Logging estruturado** dos eventos internos do serviço | **Grupo cliente** |
| **Monitoramento** da saúde do próprio serviço (health check, alertas) | **Grupo cliente** |
| **Fila de corridas** local (buffer de entrada e saída para delegação) | **Grupo cliente** |
| **Load balancer** interno entre instâncias do próprio serviço | **Grupo cliente** |

> O grupo **consome** os mecanismos de SD do Core — não os reimplementa. A responsabilidade é **integrar corretamente**, garantir que os eventos do serviço passem pelo Core como esperado, e implementar os mecanismos de infraestrutura próprios listados acima.

---

## 🗓️ Semana 1 — 08/05 a 14/05 | Back-end do Serviço de Transporte

**Foco:** Consolidar a lógica de negócio central do serviço — corridas, motoristas e passageiros.

### Tarefas:

- [ ] **Modelagem de corrida:** Garantir que a máquina de estados da corrida está implementada com as transições corretas:
  ```
  request → match → confirm → in_transit → complete
  ```
- [ ] **Gestão de motoristas:** CRUDs, disponibilidade e atribuição de corrida.
- [ ] **Gestão de passageiros:** Solicitação de corrida com origem e destino.
- [ ] **Pool de corridas:** Lógica de fila local de corridas pendentes (usada quando há delegação de entrada).
- [ ] **Política de overflow:** Definir claramente quando o serviço considera que está "congestionado" e deve delegar uma corrida (ex.: número de motoristas livres, latência, fila cheia).
- [ ] **Testes unitários** da lógica de negócio rodando no pipeline CI.

---

## 🗓️ Semana 2 — 15/05 a 21/05 | Logging, Monitoramento, Fila e Load Balancer

**Foco:** Implementar os mecanismos de infraestrutura distribuída próprios do serviço cliente.

### Logging Estruturado:

- [ ] Adotar formato estruturado (ex.: JSON) para todos os logs do serviço.
- [ ] Todo evento significativo deve gerar um log com: `timestamp`, `evento`, `corrida_id`, `servico_origem`, `estado_anterior`, `estado_novo`.
- [ ] Distinguir níveis de log: `INFO` (fluxo normal), `WARN` (degradação), `ERROR` (falha).
- [ ] Logs devem ser consultáveis e correlacionáveis com os timestamps lógicos vindos do Core.
- [ ] Expor os logs em formato compatível com a stack de auditoria do Core.

### Monitoramento e Health Check:

- [ ] Implementar endpoint `/health` que retorne o estado atual do serviço:
  - Status geral (`UP` / `DEGRADED` / `DOWN`)
  - Número de motoristas disponíveis
  - Tamanho atual da fila de corridas
  - Latência média recente
- [ ] Configurar alertas básicos (ex.: fila acima de threshold, taxa de erro elevada).
- [ ] Integrar o health check ao Docker Compose para restart automático em caso de falha.

### Fila de Corridas (Message Queue):

- [ ] Implementar fila local para desacoplar o recebimento de solicitações do processamento:
  - **Fila de entrada:** corridas recebidas por delegação aguardando atribuição a motorista.
  - **Fila de saída:** corridas que atingiram o overflow e aguardam delegação via Core.
- [ ] Garantir que a fila persiste em caso de reinício do serviço (ex.: persistência em banco ou volume Docker).
- [ ] Definir política de descarte ou reprocessamento para corridas que ficam presas na fila por tempo excessivo.

> 💡 Pode ser implementado com RabbitMQ, Kafka, Redis Streams, ou uma fila em memória com persistência — a escolha é do grupo.

### Load Balancer:

- [ ] Subir pelo menos **2 instâncias** do back-end do serviço.
- [ ] Configurar um load balancer na frente das instâncias (ex.: Nginx, Traefik, ou HAProxy via Docker Compose).
- [ ] Definir estratégia de balanceamento: round-robin, least connections, ou baseado em carga.
- [ ] Garantir que o load balancer está visível na topologia do Docker Compose do Core (o Core deve enxergar apenas o LB, não as instâncias diretamente).

---

## 🗓️ Semana 3 — 22/05 a 28/05 | Integração com o Core + Delegação

**Foco:** Conectar o serviço ao Core e implementar o fluxo de delegação para outros grupos.

### Tarefas:

- [ ] **Consumir a API do Core:** Implementar cliente HTTP/gRPC (ou o protocolo definido pelo Core) para todos os endpoints do contrato:
  - Solicitação de delegação (broadcast de leilão)
  - Recebimento de proposta (ETA + preço)
  - Confirmação de aceite
  - Notificação de status de corrida
  - Registro de eventos no log causal

- [ ] **Lógica de delegação de saída:** Quando o serviço atinge a política de overflow, chamar o Core para iniciar o leilão com outros grupos.

- [ ] **Lógica de delegação de entrada:** Receber corridas delegadas de outros grupos via Core, adicioná-las ao pool local e atribuir a um motorista disponível.

- [ ] **Testes de contrato locais:** Rodar os testes de contrato do Core contra o seu serviço antes da integração real.

- [ ] **Containerização:** Garantir que o serviço sobe corretamente com `docker compose up` do Core.

> ⚠️ **Todas as mensagens de delegação devem passar pelo Core**, nunca diretamente entre serviços.

---

## 🗓️ Semana 4 — 29/05 a 04/06 | Front-End

**Foco:** Interface funcional conectada ao back-end real.

### Telas obrigatórias:

- [ ] **Solicitar corrida:** Formulário com origem e destino.
- [ ] **Status em tempo real:** Exibir a etapa atual da corrida (aguardando, motorista a caminho, em trânsito, concluída). Atualizar em tempo real (polling ou websocket).
- [ ] **Indicação de delegação:** Quando a corrida for delegada, exibir claramente de qual grupo/serviço o motorista veio.
- [ ] **Acompanhamento do motorista:** Mapa ou indicador de progresso com ETA.
- [ ] **Histórico de corridas** (desejável).

### Qualidade esperada:

- [ ] Interface responsiva e bem projetada (não apenas funcional).
- [ ] Feedback visual para estados de espera e erros.
- [ ] Fluxo do usuário claro e sem ambiguidades.

---

## 🗓️ Semana 5 — 05/06 a 11/06 | Observabilidade + CI/CD

**Foco:** Métricas expostas e pipeline automatizado funcionando.

### Observabilidade (3,0 pts):

- [ ] Implementar endpoint de métricas no padrão definido pelo Core (compatível com Prometheus).
- [ ] Expor no mínimo:
  - Corridas locais vs. corridas delegadas para fora
  - Corridas recebidas por delegação de outros grupos
  - Latência dos endpoints de corrida
  - Throughput (requisições por segundo)
  - Estado atual do serviço (disponível / congestionado)
  - **Tamanho atual das filas de entrada e saída**
  - **Distribuição de carga entre instâncias (via load balancer)**
- [ ] Verificar que as métricas aparecem no dashboard Grafana do Core.

### CI/CD (2,0 pts):

- [ ] Pipeline com: build → testes unitários → testes de integração → deploy automatizado.
- [ ] Testes de contrato do Core executando no pipeline.
- [ ] Deploy automático ao fazer push na branch principal.

---

## 🗓️ Semana 6 — 12/06 a 18/06 | Integração entre Grupos + Resiliência

**Foco:** Sessão de integração real com todos os serviços no ar simultaneamente.

### Checklist de integração:

| Verificação                                                     | OK? |
| -----------------------------------------------------------------| -----|
| Serviço sobe via Docker Compose do Core sem intervenção         | ☐   |
| Load balancer                                                   | ☐   |
| Delegação de saída funciona (corrida vai para outro grupo)      | ☐   |
| Delegação de entrada funciona (corrida de outro grupo é aceita) | ☐   |
| Fila de entrada processa corridas delegadas sem perda           | ☐   |
| Front-end exibe de qual grupo o motorista veio                  | ☐   |
| Logs estruturados correlacionáveis com o log causal do Core     | ☐   |
| Métricas visíveis no Prometheus/Grafana do Core                 | ☐   |
| Testes de contrato passando no pipeline                         | ☐   |

### Resiliência (2,0 pts):

- [ ] Quando um grupo parceiro está fora do ar, o Circuit Breaker do Core isola a falha — verificar que **seu serviço lida bem com o fallback** retornado pelo Core (ex.: tenta outro parceiro, enfileira localmente).
- [ ] Sob carga alta, o serviço degrada graciosamente, não cai completamente.
- [ ] Compensação da Saga funciona do ponto de vista do cliente: se a delegação falha, a corrida volta ao pool local corretamente.

---

## 🗓️ Semana 7 — 19/06 | Apresentação e Avaliação Final

**Foco:** Demonstração ao vivo com stress test e injeção de falhas pelo professor.

### Roteiro sugerido para a apresentação:

1. **Demonstração do cenário feliz** — passageiro solicita corrida, motorista local aceita.
2. **Demonstração de delegação** — serviço congestionado delega para outro grupo, front-end exibe a transparência.
3. **Demonstração de falha** — grupo parceiro derrubado, fallback acionado, corrida compensada ou redelegada.
4. **Dashboards ao vivo** — mostrar métricas no Grafana durante os testes.
5. **Explicação das decisões** — arquitetura interna, política de overflow, escolhas de tecnologia.

### O que o professor vai testar:

| Cenário | O que seu serviço deve fazer |
|---------|------------------------------|
| Alto volume de requisições simultâneas | Load balancer distribui carga; fila absorve picos; serviço não cai |
| Grupo parceiro derrubado durante delegação | Lidar com fallback do Core; fila de saída retém corridas pendentes |
| Corrida delegada para o seu grupo | Fila de entrada processa; motorista é atribuído; status atualizado |
| Solicitação do log causal de uma corrida | Logs estruturados correlacionáveis com timestamps do Core |
| Derrubada de uma instância atrás do LB | LB redireciona para instância saudável; sem interrupção visível |

### Checklist final:

- [ ] Sistema estável no ambiente de integração.
- [ ] Front-end funcional e bem projetado.
- [ ] Cada membro consegue explicar o que implementou.
- [ ] `CONTRIBUTIONS.md` e peer review intra-grupo submetidos.
- [ ] Repositório documentado (arquitetura + decisões + instruções de execução).

---

## 📊 Pontuação do Grupo Cliente

| Item | Pontos | Semana-alvo |
|------|--------|-------------|
| Req. 1 a 5 — integração correta com o Core | 18,0 | Sem. 1–3 |
| Logging estruturado + monitoramento / health check | — (compõe observabilidade) | Sem. 2 |
| Fila de corridas (entrada e saída) | — (compõe resiliência) | Sem. 2 |
| Load balancer entre instâncias | — (compõe resiliência) | Sem. 2 |
| Observabilidade (métricas + Grafana) | 3,0 | Sem. 5 |
| CI/CD | 2,0 | Sem. 5 |
| Front-end (funcionalidade + design) | 4,0 | Sem. 4 |
| Resiliência sob stress | 2,0 | Sem. 6 |
| Interoperabilidade entre serviços | 3,0 | Sem. 6 |
| Apresentação oral | 3,0 | Sem. 7 |
| Qualidade da spec do Core (compartilhada) | 5,0 | — |
| **Total** | **40,0** | |

---

> **Deadline absoluto para pendências:** 12/06/2026  
---
