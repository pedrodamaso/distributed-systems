# Capítulo 6 — Comunicação Indireta
## Material Teórico para Sistemas Distribuídos
**Referência:** Coulouris, G. et al. *Sistemas Distribuídos: Conceitos e Projeto*, 5ª ed. Bookman, 2013.

---

## Objetivos de Aprendizagem

Ao final deste capítulo, o estudante deverá ser capaz de:

- Distinguir comunicação direta (Cap. 4 e 5) de comunicação indireta e explicar as propriedades de desacoplamento espacial e temporal
- Descrever o modelo de comunicação em grupo: garantias de confiabilidade (integridade, validade, acordo) e ordenação (FIFO, causal, total)
- Explicar o paradigma publicar-assinar com seus quatro modelos de assinatura e estratégias de roteamento distribuído
- Caracterizar o modelo de filas de mensagem (MOM) e seus casos de uso em integração empresarial
- Diferenciar memória compartilhada distribuída (DSM) e espaços de tuplas como abstrações de estado compartilhado
- Comparar os cinco estilos de comunicação indireta segundo desacoplamento, padrão, escala e objetivo

---

## Pré-requisitos

- Multicast IP (Cap. 4, Seção 4.4) — mecanismo de base para comunicação em grupo
- Passagem de mensagens e protocolos de requisição-resposta (Cap. 4 e 5)
- Modelo de falhas (Cap. 2, Seção 2.4): omissão, colapso, byzantine
- Noções de programação orientada a objetos e interfaces Java

---

## 6.1 Introdução: Desacoplamento Espacial e Temporal

### 6.1.1 Definição

**Comunicação indireta:** comunicação por meio de um **intermediário**, sem acoplamento direto entre remetente e destinatário(s).

**Consequências:**
- **Desacoplamento espacial:** remetente não conhece a identidade do destinatário e vice-versa
- **Desacoplamento temporal:** remetente e destinatário podem ter **tempos de vida independentes** — o destinatário pode não existir no momento do envio

### 6.1.2 Tabela de Acoplamento

| | Acoplamento temporal | Desacoplamento temporal |
|---|---|---|
| **Acoplamento espacial** | Passagem de mensagens, invocação remota (Caps. 4 e 5) | RPC enfileirado (intermediário armazena) |
| **Desacoplamento espacial** | Multicast IP (destinatários devem existir no momento) | **Maioria dos paradigmas indiretos** (este capítulo) |

> **Distinção importante:** comunicação **assíncrona** (remetente não bloqueia) ≠ **desacoplamento temporal** (destinatário pode não existir). São conceitos ortogonais.

### 6.1.3 Vantagens e Desvantagens

| Vantagens | Desvantagens |
|-----------|--------------|
| Flexibilidade para lidar com mudanças (substitui, atualiza, migra componentes) | Overhead de desempenho pelo nível extra de indireção |
| Tolerância a falhas (remetente continua mesmo se destinatário falha) | Sistemas mais difíceis de gerenciar (sem acoplamento direto) |
| Suporte natural a ambientes dinâmicos e voláteis | — |

---

## 6.2 Comunicação em Grupo

### 6.2.1 Modelo de Programação

A comunicação em grupo oferece uma abstração sobre multicast: uma operação envia para todos os membros do grupo.

| Conceito | Descrição |
|----------|-----------|
| **Unicast** | Comunicação ponto a ponto (1 → 1) |
| **Multicast (grupo)** | 1 operação envia para N membros do grupo |
| **Broadcast** | 1 → todos os processos no sistema |
| **Grupo** | Conjunto de processos com participação dinâmica (ingressar/sair/falhar) |

**Vantagem de eficiência:** uma única operação de multicast permite uso eficiente de largura de banda e evita inconsistências que ocorrem com N envios independentes (se remetente falha no meio, parte dos membros recebe e parte não).

**Grupos de processos vs grupos de objetos:**
- **Grupos de processos:** nível baixo (semelhante a sockets); mensagens são vetores de bytes; sem suporte a empacotamento de tipos complexos
- **Grupos de objetos:** nível alto; proxy local encaminha invocações para todos os membros; parâmetros empacotados como na RMI (ex: Electra, CORBA)

**Outras distinções:**

| Dimensão | Variante A | Variante B |
|----------|-----------|-----------|
| Participação | **Fechado** — só membros enviam para o grupo | **Aberto** — qualquer processo envia para o grupo |
| Sobreposição | **Não sobrepostos** — processo em no máximo 1 grupo | **Sobrepostos** — processo em múltiplos grupos |
| Sincronismo | Síncrono | Assíncrono |

---

### 6.2.2 Garantias de Confiabilidade e Ordenação

**Multicast confiável** exige três propriedades (além das de comunicação 1:1):

| Propriedade | Definição |
|-------------|-----------|
| **Integridade** | Mensagem recebida é idêntica à enviada; nenhuma mensagem entregue duas vezes |
| **Validade** | Toda mensagem enviada será entregue |
| **Acordo** | Se uma mensagem é entregue a algum processo, então é entregue a **todos** os processos do grupo |

**Ordenação de mensagens:**

| Tipo | Garantia |
|------|---------|
| **FIFO (ordem de origem)** | Se processo P envia M1 antes de M2, todos os membros entregam M1 antes de M2 |
| **Causal** | Se M1 acontece-antes de M2 (relação causal), todos entregam M1 antes de M2 |
| **Total** | Se qualquer processo entrega M1 antes de M2, então **todos** entregam M1 antes de M2 |

> **Hierarquia:** Total ⊃ Causal ⊃ FIFO (total implica causal implica FIFO, mas não o inverso).

---

### 6.2.3 Gerenciamento de Participação no Grupo

Quatro tarefas do serviço de participação:

1. **Interface para mudanças:** operações para criar/destruir grupos, adicionar/retirar processo
2. **Detecção de falha:** monitora membros; marca como *Suspeito* ou *Não suspeito*; exclui suspeitos
3. **Notificação de mudanças:** avisa membros quando alguém entra, sai ou é excluído por falha
4. **Expansão de endereço de grupo:** traduz identificador de grupo → lista de membros atuais; coordena entrega mesmo durante mudanças de participação

> **Multicast IP** realiza expansão de endereço, mas **não** notifica membros sobre participação atual e **não** coordena entrega com mudanças — é um caso frágil de serviço de grupo.

---

### 6.2.4 Estudo de Caso: JGroups

JGroups é um toolkit Java para comunicação em grupo confiável (de código aberto, parte do JBoss).

**Arquitetura em três camadas:**

```
┌─────────────────────────────┐
│         Aplicações          │
├─────────────────────────────┤
│    Blocos de Construção     │  ← abstrações de alto nível
├─────────────────────────────┤
│       Canal (JChannel)      │  ← interface principal
├─────────────────────────────┤
│     Pilha de Protocolos     │  ← camadas compostas
│  CAUSAL / GMS / MERGE /     │
│  FRAG / UDP                 │
└─────────────────────────────┘
```

**Canal (JChannel):**
- `connect(nomeDo Grupo)` — ingressa no grupo (cria se não existe)
- `send(msg)` — envia por multicast confiável para todos os membros
- `receive(timeout)` — recebe mensagem (bloqueia se 0)
- `getView()` — retorna visão atual (lista de membros)
- `getState()` — retorna estado histórico do grupo

```java
// Produtor (alarme de incêndio)
JChannel channel = new JChannel();
channel.connect("AlarmChannel");
Message msg = new Message(null, null, "Fire!");
channel.send(msg);

// Consumidor
JChannel channel = new JChannel();
channel.connect("AlarmChannel");
Message msg = (Message) channel.receive(0);  // bloqueia
```

**Blocos de construção:**

| Bloco | Função |
|-------|--------|
| `MessageDispatcher` | Envia para grupo e bloqueia até receber N respostas (maioria ou todas) |
| `RpcDispatcher` | Invoca método em todos os objetos do grupo; aguarda respostas |
| `NotificationBus` | Barramento de eventos distribuído; usado para consistência de caches |

**Pilha de protocolos (exemplo):**

| Camada | Função |
|--------|--------|
| `UDP` | Transporte; usa multicast IP ou datagramas UDP unicast |
| `FRAG` | Fragmentação de mensagens (padrão: 8.192 bytes) |
| `MERGE` | Lida com particionamentos de rede e subsequente mesclagem de subgrupos |
| `GMS` | Gerenciamento de participação com membro do grupo (visões coerentes) |
| `CAUSAL` | Ordenação causal de mensagens |

---

## 6.3 Sistemas Publicar-Assinar

### 6.3.1 Modelo de Programação

Paradigma de comunicação de **um para muitos** baseado em eventos.

**Operações:**

| Operação | Papel | Descrição |
|----------|-------|-----------|
| `publish(e)` | Publicador | Divulga evento e |
| `subscribe(f)` | Assinante | Registra interesse: filtro f sobre o conjunto de eventos |
| `unsubscribe(f)` | Assinante | Revoga assinatura |
| `notify(e)` | Sistema → Assinante | Entrega evento correspondente |
| `advertise(f)` | Publicador (opcional) | Declara antecipadamente os tipos de eventos que gerará |

**Características:**
- **Heterogeneidade:** componentes que não foram projetados juntos podem interagir via eventos
- **Assincronicidade:** publicadores não precisam sincronizar com assinantes

---

### 6.3.2 Modelos de Assinatura (Filtros)

Em ordem crescente de sofisticação:

| Modelo | Como a assinatura é expressa | Exemplo |
|--------|------------------------------|---------|
| **Baseado em canal** | Assina um canal nomeado; recebe tudo que vai para ele | `subscribe("AlarmChannel")` |
| **Baseado em tópico** | Campo específico da mensagem (o tópico) define o filtro; suporta hierarquia | `subscribe("financas/acoes")` |
| **Baseado em conteúdo** | Consulta sobre múltiplos campos do evento (predicados) | `subscribe("tópico='SD' AND autor='Coulouris'")` |
| **Baseado em tipo** | Filtro definido por tipo/subtipo do evento; integra-se à linguagem de tipos | `subscribe(TipoAlertaSistema.class)` |

> **Processamento de evento complexo (CEP):** sistemas avançados permitem padrões sobre sequências temporais de eventos — ex: "se ação X subir 5% nos últimos 10 minutos, notifique". Útil em sistemas financeiros, monitoramento de infraestrutura.

---

### 6.3.3 Implementação e Roteamento de Eventos

**Arquitetura em camadas:**

```
┌──────────────────────────────────────────────────────┐
│  Correspondência (matching: assinatura ↔ evento)     │
├──────────────────────────────────────────────────────┤
│  Roteamento de evento                                │
│  (garante entrega eficiente aos assinantes corretos) │
├──────────────────────────────────────────────────────┤
│  Infraestrutura de sobreposição                      │
│  (rede de intermediários ou P2P)                     │
├──────────────────────────────────────────────────────┤
│  Protocolos de rede: TCP/IP · Multicast IP · 802.11  │
└──────────────────────────────────────────────────────┘
```

**Estratégias de implementação:**

| Estratégia | Descrição | Vantagem | Desvantagem |
|------------|-----------|----------|-------------|
| **Centralizada** | Único servidor intermediário | Simples | Ponto único de falha; gargalo |
| **Rede de intermediários** | Vários intermediários cooperam | Tolerância a falhas; escalável | Maior complexidade |
| **P2P (sem distinção)** | Todos os nós são publicadores, assinantes e intermediários | Alta escalabilidade | Complexidade de roteamento |

**Algoritmos de roteamento:**

| Estratégia | Mecanismo | Eficiência |
|------------|-----------|------------|
| **Inundação** | Envia notificação para todos os nós; correspondência no destinatário | Simples, mas alto tráfego |
| **Filtragem (CBR)** | Intermediários propagam assinaturas; encaminham só onde há assinante válido | Eficiente para eventos frequentes |
| **Anúncios** | Publicadores anunciam tipos de eventos antecipadamente; reduz propagação de assinaturas | Bom equilíbrio carga |
| **Rendez-vous** | Espaço de eventos particionado entre nós; SN(s) e EN(e) mapeiam para nós responsáveis | Balanceamento de carga natural |
| **Fofoca informada** | Troca periódica e probabilística de eventos entre vizinhos; considera conteúdo | Bom para ambientes dinâmicos |

**Exemplos de sistemas publicar-assinar:**

| Sistema | Assinatura | Distribuição | Roteamento |
|---------|-----------|-------------|------------|
| CORBA Event Service | Canal | Centralizado | — |
| TIB Rendezvous | Tópico | Distribuído | Filtragem |
| Scribe | Tópico | P2P (DHT) | Rendez-vous |
| Siena | Conteúdo | Distribuído | Filtragem |
| Gryphon | Conteúdo | Distribuído | Filtragem |
| Hermes | Tópico + conteúdo | Distribuído | Rendez-vous + filtragem |

---

## 6.4 Filas de Mensagem (Message-Oriented Middleware)

### 6.4.1 Modelo de Programação

Comunicação **ponto a ponto** indireta via fila persistente — o intermediário é a própria fila.

```
Produtores       Sistema de Fila        Consumidores
   │                    │                    │
   │─── envia ─────────►│                    │
   │                    │─── recebe ─────────►│
   │                    │◄─── consulta ───────│
   │                    │─── notifica ───────►│
```

**Três estilos de recepção:**
- **Bloqueante:** bloqueia até mensagem disponível
- **Não bloqueante (consulta):** retorna mensagem se disponível, ou indicação de indisponível
- **Notificação:** emite evento quando mensagem chega na fila

**Estrutura de uma mensagem:**

| Campo | Conteúdo |
|-------|----------|
| **Destino** | Identificador único da fila de destino |
| **Metadados** | Prioridade, modo de entrega, timestamp, TTL, ID de mensagem |
| **Corpo** | Opaco para o sistema; serializado (tipos empacotados, objeto Java, XML) |

**Propriedades fundamentais:**
- **Persistência:** mensagens armazenadas indefinidamente (até serem consumidas) e em disco
- **Confiabilidade:** toda mensagem enviada é entregue exatamente uma vez (validade + integridade)
- **Sem garantia de prazo:** o sistema garante entrega, mas não quando

**Funcionalidades adicionais:**
- **Transações:** envio/recebimento dentro de transação (semântica tudo-ou-nada)
- **Transformação de mensagem:** conversão de formato entre sistemas heterogêneos (ex: SOAP ↔ IIOP)
- **Segurança:** SSL, autenticação, controle de acesso (ex: WebSphere MQ)

---

### 6.4.2 Estudo de Caso: WebSphere MQ (IBM)

| Componente | Função |
|------------|--------|
| **Gerenciador de fila (QM)** | Hospeda filas; aceita conexões via MQI |
| **MQI (Message Queue Interface)** | API: `MQCONN`, `MQDISC`, `MQPUT`, `MQGET` |
| **Canal cliente** | Conexão QM ↔ aplicativo cliente (usa proxy + RPC) |
| **Canal de mensagem** | Conexão QM ↔ QM para encaminhamento assíncrono de mensagens |
| **MCA (Message Channel Agent)** | Gerencia canal de mensagem em cada extremidade |

**Topologia hub-and-spoke:**
```
[Clientes] → [Estrela (spoke)] → [Hub (QM central)] → [Serviços]
                                       ↕
                               [Outras estrelas]
```
- **Hub:** hospeda serviços; nó com recursos suficientes para o tráfego
- **Estrelas:** próximas aos clientes; alta largura de banda para o hub
- **Comunicação:** cliente → estrela via RPC (bloqueante); estrela → hub via canal assíncrono (confiável)

---

### 6.4.3 Estudo de Caso: JMS (Java Messaging Service)

JMS é uma especificação Java que unifica publicar-assinar e filas de mensagem.

**Papéis:**
- **Cliente JMS:** produtor ou consumidor
- **Provedor JMS:** implementação da especificação (Joram, ActiveMQ, OpenMQ, JBoss MQ…)
- **Destino JMS:** Tópico (`Topic`) ou Fila (`Queue`)

**Modelo de programação:**
```
FábricaConexão → Conexão → Sessão → {Produtor | Consumidor}
                                          ↓
                                    Tópico ou Fila
```

**Exemplo (alarme de incêndio — publicador):**
```java
Context ctx = new InitialContext();
TopicConnectionFactory factory = (TopicConnectionFactory) ctx.lookup("TopicConnectionFactory");
Topic topic = (Topic) ctx.lookup("Alarms");
TopicConnection conn = factory.createTopicConnection();
TopicSession sess = conn.createTopicSession(false, Session.AUTO_ACKNOWLEDGE);
TopicPublisher pub = sess.createPublisher(topic);
TextMessage msg = sess.createTextMessage();
msg.setText("Fire!");
pub.publish(msg);
```

**Exemplo (consumidor):**
```java
TopicSubscriber sub = sess.createSubscriber(topic);
sub.start();
TextMessage msg = (TextMessage) sub.receive();  // bloqueia
```

**Seletor de mensagem:** filtro SQL sobre metadados da mensagem (não o corpo):
```java
// Receber apenas alarmes de determinado local
TopicSubscriber sub = sess.createSubscriber(topic, "location = 'Bloco-A'", false);
```

> **JMS unifica** os dois paradigmas: `TopicConnection` → publicar-assinar (1:N); `QueueConnection` → filas de mensagem (1:1). A separação é obrigatória dentro de uma conexão.

---

## 6.5 Estratégias de Memória Compartilhada

### 6.5.1 Memória Compartilhada Distribuída (DSM)

**Definição:** abstração que permite a processos em computadores distintos acessar uma memória aparentemente compartilhada, sem que ela seja fisicamente compartilhada.

```
Processo A           Processo B           Processo C
┌──────────┐        ┌──────────┐        ┌──────────┐
│ [DSM]    │←──────►│ [DSM]    │←──────►│ [DSM]    │
│ var x=5  │  sync  │ var x=?  │  sync  │ var x=5  │
└──────────┘        └──────────┘        └──────────┘
  Memória física     Memória física     Memória física
     (nó 1)             (nó 2)             (nó 3)
```

**Comparativo DSM vs Passagem de Mensagens:**

| Aspecto | DSM | Passagem de Mensagens |
|---------|-----|-----------------------|
| Empacotamento | Não necessário (variáveis compartilhadas diretamente) | Necessário (serialização) |
| Visibilidade do custo | Oculta (qualquer acesso pode ou não envolver rede) | Explícita (toda comunicação é uma operação send/receive) |
| Proteção | Menor (processos podem corromper estado alheio) | Maior (espaços de endereçamento privativos) |
| Sincronização | Travas, semáforos, barreiras | Primitivas de mensagem (bloqueio/desbloqueio) |
| Heterogeneidade | Problema com diferentes representações de int/float | Empacotamento cuida das diferenças |
| Persistência | Possível (DSM pode outlive processos individuais) | Geralmente não (a não ser com filas) |

**Aplicação típica:** computação paralela/HPC; multiprocessadores NUMA (Non-Uniform Memory Access).

---

### 6.5.2 Comunicação via Espaço de Tuplas (Linda / JavaSpaces)

**Modelo:** processos comunicam-se escrevendo e lendo **tuplas** de um espaço compartilhado.

**Operações fundamentais:**

| Operação | Descrição |
|----------|-----------|
| `write(t)` | Insere tupla t no espaço (não afeta outras tuplas) |
| `read(spec)` | Retorna cópia de uma tupla que corresponde a spec (bloqueia até haver correspondência) |
| `take(spec)` | Retorna e **remove** tupla correspondente a spec (bloqueia até haver correspondência) |

**Correspondência associativa (por conteúdo):**
```
Espaço de tuplas:
  <"Capital", "Scotland", "Edinburgh">
  <"Capital", "Wales", "Cardiff">
  <"Population", "Scotland", 5168000>
  <"Population", "UK", 61000000>

take(<String, "Scotland", String>)   → remove <"Capital", "Scotland", "Edinburgh">
take(<String, "Scotland", Integer>)  → remove <"Population", "Scotland", 5168000>
read(<"Population", String, Integer>) → retorna qualquer tupla de população (não determinístico)
```

**Propriedades:**
- **Desacoplamento espacial:** remetente não sabe quem vai consumir a tupla
- **Desacoplamento temporal:** tupla persiste no espaço até ser removida; produtor e consumidor não precisam coexistir

**Tuplas são imutáveis** — para modificar, deve-se usar `take` e `write`:
```
<s, count> := myTS.take(<"counter", integer>);
myTS.write(<"counter", count+1>);
```

---

### 6.5.3 Implementação Distribuída de Espaços de Tuplas

| Estratégia | Mecanismo | Vantagem | Desvantagem |
|------------|-----------|----------|-------------|
| **Centralizada** | Único servidor | Simples | Ponto único de falha; não escala |
| **Replicação** (Xu & Liskov) | Todas as réplicas têm cópia de todas as tuplas; multicast para `write`; fase 1+2 para `take` | Tolerância a falhas | Protocolo complexo para `take` (2 fases + travas) |
| **Particionamento** (York Linda Kernel) | Hash mapeia cada tupla para um TSS (Tuple Space Server); sem replicação | Alto desempenho para computação paralela | `read`/`take` exigem busca linear |
| **P2P** (PeerSpaces, LIME) | Todos os nós cooperam | Escalabilidade e disponibilidade intrínsicas | Complexidade |

**Algoritmo de `take` replicado (2 fases — Xu & Liskov):**
```
Fase 1 (seleção):
  1. Multicast da especificação para todas as réplicas
  2. Cada réplica adquire trava no conjunto de tuplas; responde com tuplas correspondentes
  3. Repete até todas aceitarem; seleciona tupla da interseção
Fase 2 (remoção):
  1. Multicast "remove tupla T" para todas as réplicas
  2. Réplicas removem T, confirmam, liberam trava
  3. Repete até todas confirmarem
```

---

### 6.5.4 Estudo de Caso: JavaSpaces

JavaSpaces (Sun/Jini) estende o modelo Linda para o mundo orientado a objetos:
- **Entrada** (*Entry*) = objeto Java (`implements net.jini.core.entry.Entry`)
- Permite comportamento associado (métodos), não apenas dados

**API JavaSpaces:**

| Operação | Descrição |
|----------|-----------|
| `write(entry, txn, lease)` | Insere entrada; lease define duração (ou `FOREVER`) |
| `read(template, txn, timeout)` | Retorna cópia de entrada correspondente (bloqueia) |
| `readIfExists(template, txn, timeout)` | Como `read`, mas não bloqueia; retorna null se inexistente |
| `take(template, txn, timeout)` | Remove e retorna entrada correspondente (bloqueia) |
| `takeIfExists(template, txn, timeout)` | Como `take`, não bloqueante |
| `notify(template, txn, listener, lease, handback)` | Notifica via `RemoteEventListener` quando entrada correspondente é inserida |

**Correspondência:** entrada E corresponde ao template T se E é da **mesma classe (ou subclasse)** de T e todos os campos não-null de T correspondem exatamente aos de E.

**Transações:** operações podem ser agrupadas em transação distribuída (tudo ou nada, podendo abranger múltiplos JavaSpaces).

**Exemplo (alarme de incêndio):**
```java
// Produtor
JavaSpace space = SpaceAccessor.findSpace("AlarmSpace");
AlarmTupleJS tuple = new AlarmTupleJS("Fire!");
space.write(tuple, null, 60*60*1000);  // persiste 1 hora

// Consumidor
AlarmTupleJS template = new AlarmTupleJS("Fire!");
AlarmTupleJS recvd = (AlarmTupleJS) space.read(template, null, Long.MAX_VALUE);
```

---

## Comparativo dos Cinco Estilos de Comunicação Indireta

| Aspecto | Grupos | Publicar-Assinar | Filas de Mensagem | DSM | Espaços de Tuplas |
|---------|--------|-----------------|-------------------|-----|-------------------|
| **Desacoplado no espaço** | Sim | Sim | Sim | Sim | Sim |
| **Desacoplado no tempo** | Possível | Possível | **Sim** | **Sim** | **Sim** |
| **Estilo de serviço** | Comunicação | Comunicação | Comunicação | **Estado** | **Estado** |
| **Padrão de comunicação** | 1 para N | 1 para N | **1 para 1** | 1 para N | 1:1 ou 1:N |
| **Principal objetivo** | SD confiável; tolerância a falhas | Disseminação de informações; EAI; ubíquo | EAI; processamento de transações; disseminação | Computação paralela e distribuída | Computação paralela; ubíquo |
| **Escalabilidade** | **Limitada** (manutenção de visão do grupo) | Possível | Possível | **Limitada** | **Limitada** (operação `take`) |
| **Endereçamento associativo** | Não | Só baseado em conteúdo | Não | Não | **Sim** |

---

## Mapa Conceitual do Capítulo

```
                      COMUNICAÇÃO INDIRETA
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
   Baseado em          Baseado em         Baseado em
  Comunicação         Comunicação           Estado
          │                  │                  │
     ┌────┤           ┌──────┤           ┌──────┤
     │    │           │      │           │      │
   Grupos Pub-Sub  Filas    JMS         DSM  Espaços
  (6.2)  (6.3)    (6.4)                (6.5.1) de Tuplas
     │      │       │                         (6.5.2)
  JGroups  Modelos Websphere               Linda/
  Canais   assinatura  MQ                 JavaSpaces
  Blocos   Canal      Hub-and-          write/read/take
  Pilha    Tópico     spoke             Associativo
  Proto.   Conteúdo
           Tipo
              │
          Roteamento:
          Inundação
          Filtragem (CBR)
          Rendez-vous (DHT)
          Fofoca informada
```

---

## Relevância para Sistemas de Informação

| Área de SI | Conexão com o Capítulo 6 |
|------------|--------------------------|
| **Desenvolvimento de Sistemas** | Event-driven architecture (EDA), microsserviços com event bus, padrão Observer/Event Listener são instâncias de publicar-assinar |
| **Banco de Dados** | Message brokers integram sistemas legados (EAI); Oracle AQ usa filas como tabelas SQL; CDC (Change Data Capture) é publicar-assinar sobre DB |
| **Engenharia de Software** | Padrão arquitetural de filas de mensagem (ex: Kafka, RabbitMQ, SQS) é fundamental em arquiteturas de microsserviços; desacoplamento espacial/temporal facilita manutenção |
| **Segurança da Informação** | Auditoria e SIEM (Security Information and Event Management) são sistemas publicar-assinar; logs são escritos em filas persistentes |
| **Gestão de TI** | ITSM, monitoramento de infraestrutura (Prometheus, Grafana) usam publicar-assinar; alertas via filas garantem persistência |
| **Computação em Nuvem** | AWS SNS/SQS, Azure Service Bus, Google Pub/Sub são implementações cloud-native dos paradigmas deste capítulo |
| **Computação Ubíqua e IoT** | Dispositivos IoT publicam eventos de sensor; MQTT é protocolo publicar-assinar para IoT; espaços de tuplas usados em ambientes dinâmicos |
| **Arquitetura Empresarial** | EAI (Enterprise Application Integration) é o principal caso de uso das filas de mensagem comerciais (WebSphere MQ, MSMQ) |
| **Analytics e BI** | Processamento de streams (Kafka Streams, Apache Flink) é publicar-assinar com CEP; pipeline de dados assíncrono usa filas |

---

## Erros Comuns e Confusões

| Erro | Confusão | Correção |
|------|----------|----------|
| "Comunicação assíncrona = desacoplamento temporal" | Assíncrono = remetente não bloqueia; temporal = destinatário pode não existir | São ortogonais; UDP é assíncrono mas acoplado no tempo (destinatário deve estar ativo) |
| "Multicast IP já oferece comunicação em grupo confiável" | Multicast IP tem semântica UDP (falhas por omissão) | Comunicação em grupo adiciona acordo, ordenação e gerenciamento de participação sobre multicast IP |
| "FIFO, causal e total são equivalentes" | FIFO preserva ordem do remetente; total garante mesma ordem global | FIFO ⊆ Causal ⊆ Total — são garantias progressivamente mais fortes |
| "Pub-sub baseado em tópico e baseado em canal são iguais" | Funcionalmente semelhantes, mas tópicos são declarados explicitamente e podem ter hierarquia | Canal = nomeado fisicamente; tópico = campo na mensagem, com estrutura hierárquica |
| "Filas de mensagem são só para comunicação 1:1" | Filas são 1:1 (ponto a ponto), mas JMS integra pub-sub e filas | A distinção é importante: filas garantem que cada mensagem é consumida uma única vez |
| "DSM elimina a necessidade de coordenação" | DSM ainda exige travas e semáforos para acessos concorrentes | DSM oculta a passagem de mensagens, mas não a sincronização |
| "`take` e `read` em espaços de tuplas têm o mesmo efeito" | `read` deixa a tupla no espaço; `take` a remove | Sem `take`, espaço de tuplas seria semelhante a pub-sub; `take` é a operação "destrutiva" |

---

## Questões de Revisão

1. Explique a diferença entre desacoplamento espacial e temporal. Por que o multicast IP é desacoplado no espaço mas acoplado no tempo?

2. Por que a comunicação em grupo adiciona a propriedade de **acordo** às propriedades de integridade e validade já existentes na comunicação ponto a ponto confiável?

3. Dê um exemplo concreto de sequência de mensagens que satisfaz ordenação FIFO mas não ordenação total. Depois, dê um exemplo que satisfaz ordenação causal mas não total.

4. No JGroups, qual a diferença entre usar o canal (`JChannel`) diretamente e usar o bloco de construção `RpcDispatcher`?

5. Considere um sistema de leilão online onde múltiplos usuários dão lances. Qual modelo de assinatura (canal, tópico, conteúdo, tipo) seria mais adequado para notificar usuários que o lance atual superou seu lance máximo? Justifique.

6. Compare as estratégias de roteamento **por filtragem** e **rendez-vous** em um sistema publicar-assinar baseado em conteúdo. Quais são os trade-offs em termos de tráfego de rede e balanceamento de carga?

7. Por que filas de mensagem obtêm desacoplamento temporal enquanto multicast IP não? Qual propriedade fundamental diferencia os dois?

8. No WebSphere MQ com topologia hub-and-spoke, por que a comunicação entre cliente e estrela usa RPC (bloqueante), mas entre estrelas e hub usa canais assíncronos?

9. Compare DSM e passagem de mensagens em termos de visibilidade do custo de comunicação. Qual é mais seguro para programas paralelos com muitos escritores? Por quê?

10. Explique por que a operação `take` em espaços de tuplas distribuídos replicados (Xu & Liskov) requer um protocolo de 2 fases, enquanto `write` e `read` são mais simples. O que tornaria `take` desnecessária e o que o espaço de tuplas sem `take` se assemelharia?

---

## Referência

> COULOURIS, G.; DOLLIMORE, J.; KINDBERG, T.; BLAIR, G. **Sistemas Distribuídos: Conceitos e Projeto**. 5. ed. Porto Alegre: Bookman, 2013. Capítulo 6, p. 229-278.
