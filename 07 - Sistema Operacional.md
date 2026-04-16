# Capítulo 7 — Sistema Operacional
## Material Teórico para Sistemas Distribuídos

---

## Objetivos de Aprendizagem

Ao final deste capítulo, o aluno deverá ser capaz de:

1. Explicar o papel da camada de sistema operacional em sistemas distribuídos
2. Distinguir processos de threads e justificar o uso de multithreading em servidores
3. Descrever as arquiteturas de servidores multithreaded e seus trade-offs
4. Analisar os custos de invocação remota e as otimizações possíveis (LRPC, memória compartilhada)
5. Comparar núcleos monolíticos e micronúcleos no contexto de sistemas distribuídos
6. Explicar os fundamentos de virtualização e paravirtualização
7. Descrever a arquitetura do Xen: hipervisor, domínios, escalonadores e drivers divididos

---

## Pré-requisitos Recomendados

- Conceitos básicos de sistemas operacionais: processos, escalonamento, memória virtual
- Capítulo 4 (IPC): sockets, comunicação entre processos
- Capítulo 5 (RPC/RMI): invocação remota, stubs, marshalling

---

## 7.1 A Camada do Sistema Operacional

Em sistemas distribuídos, cada nó executa um **sistema operacional de rede** (UNIX, Windows), não um SO distribuído. A combinação **middleware + SO de rede** equilibra:

- **Autonomia local**: cada nó gerencia seus recursos independentemente
- **Acesso transparente**: o middleware expõe serviços distribuídos via abstrações do SO

```
┌─────────────────────────────────────────────────────┐
│           Aplicativos, Serviços                      │
├─────────────────────────────────────────────────────┤
│              Middleware                              │
├──────────────────────┬──────────────────────────────┤
│  SO: Nó 1            │  SO: Nó 2                    │
│  (núcleo + libs)     │  (núcleo + libs)             │
├──────────────────────┼──────────────────────────────┤
│  Hardware/Rede 1     │  Hardware/Rede 2             │
└──────────────────────┴──────────────────────────────┘
```

**Componentes básicos do SO** relevantes para SD:

| Componente | Função |
|---|---|
| Gerência de processos | Criação de processos, ambientes de execução |
| Gerência de threads | Criação, sincronização, escalonamento de threads |
| Gerência de comunicação | IPC local; sockets para comunicação externa |
| Gerência de memória | Memória física e virtual, paginação |
| Supervisor (HAL) | Interrupções, chamadas de sistema, MMU |

**Requisitos para gerenciadores de recursos**:
- **Encapsulamento**: interface de serviço útil, ocultando detalhes internos
- **Proteção**: acesso restrito apenas a clientes autorizados
- **Processamento concorrente**: múltiplos clientes acessam recursos simultaneamente

---

## 7.2 Proteção

O núcleo usa hardware para proteger recursos contra acessos ilegítimos.

**Modos de operação do processador**:

| Modo | Nível de privilégio | Quem executa |
|---|---|---|
| Supervisor (privilegiado) | Completo | Núcleo |
| Usuário (não privilegiado) | Restrito | Processos de aplicação |

**Mecanismo de proteção**:
- **Espaço de endereçamento**: isolamento entre processos via MMU
- **Chamada de sistema (TRAP)**: instrução que eleva o processador para modo supervisor, executa serviço do núcleo e retorna ao modo usuário
- **Custo da proteção**: troca de contexto ao cruzar limite usuário ↔ núcleo consome centenas de ciclos

**Alternativa via linguagem**: linguagens fortemente tipadas (Modula-3, Sing#/C#) evitam acessos arbitrários a ponteiros, permitindo proteção sem hardware.

---

## 7.3 Processos e Threads

### 7.3.1 Definições

**Processo** = ambiente de execução + uma ou mais threads

```
Processo
├── Espaço de endereçamento
├── Interfaces de comunicação (sockets, semáforos)
├── Recursos de alto nível (arquivos abertos, janelas)
└── Threads: T1, T2, ..., Tn
```

**Thread** = abstração de atividade (fluxo de execução) dentro de um processo

### 7.3.2 Espaços de Endereçamento

Um espaço de endereçamento contém **regiões** não sobrepostas, cada uma com:
- extensão (endereço base + tamanho)
- permissões (leitura/escrita/execução)
- capacidade de crescimento

**Regiões compartilhadas**: mesma memória física mapeada em múltiplos espaços de endereçamento. Usos:
- Compartilhamento de bibliotecas (uma cópia para vários processos)
- Mapeamento do núcleo (evita troca de mapeamentos em chamadas de sistema)
- Comunicação eficiente entre processos (sem cópia de mensagens)

**Cópia na escrita (copy-on-write)**:
- Região herdada é *logicamente* copiada no fork, mas fisicamente compartilhada
- Cópia física ocorre somente quando um processo tenta escrever
- Otimiza criação de processos (evita cópia imediata de páginas)

### 7.3.3 Criação de Processos

Em sistemas distribuídos, criação de processo envolve dois aspectos independentes:

**1. Escolha do host (políticas de balanceamento de carga)**

| Política | Descrição |
|---|---|
| Transferência | Decide se o processo roda local ou remotamente |
| Localização | Escolhe qual nó recebe o processo transferido |

**Estratégias de balanceamento**:
- **Iniciada pela origem**: nó com carga alta empurra processo para outro
- **Iniciada pelo destino**: nó com carga baixa anuncia disponibilidade
- **Migração de processo**: transfere processo *em execução* entre nós (cara, raramente usada)

**Topologias de gerenciamento de carga**:

```
Centralizado        Hierárquico         Descentralizado
    [GM]            [GM]                  Nó1 ↔ Nó2
   / | \           /   \                  ↕       ↕
 N1 N2 N3       [GM]  [GM]              Nó3 ↔ Nó4
                /\     /\
               N1 N2  N3 N4
```

**2. Criação do ambiente de execução**: inicializar espaço de endereçamento (formato estático ou herdado via fork + copy-on-write).

### 7.3.4 Threads

**Por que usar múltiplas threads?**
- Sobrepor computação com E/S
- Explorar paralelismo em multiprocessadores
- Evitar bloqueio total do servidor enquanto aguarda operações de disco/rede

**Exemplo de throughput de servidor** (2ms processamento + 8ms E/S/pedido):

| Configuração | Throughput máximo |
|---|---|
| 1 thread, sem cache | 100 pedidos/s |
| 2 threads, sem cache, disco serializado | 125 pedidos/s |
| N threads, cache 75%, limitado por E/S | 500 pedidos/s |
| N threads, cache 75%, limitado por CPU | 400 pedidos/s |

### 7.3.5 Arquiteturas de Servidores Multithreaded

```
┌─────────────────────────────────────────────────────────────────┐
│          Arquiteturas Baseadas em Threads (CORBA ORBs)          │
├──────────────────┬──────────────────┬───────────────────────────┤
│ Conjunto de      │ Thread por       │ Thread por conexão ou     │
│ Trabalhadores    │ Pedido           │ Thread por Objeto         │
├──────────────────┼──────────────────┼───────────────────────────┤
│ Pool fixo de     │ Nova thread por  │ Thread vive enquanto      │
│ threads + fila   │ pedido; termina  │ conexão/objeto existir    │
│ compartilhada    │ ao concluir      │                           │
├──────────────────┼──────────────────┼───────────────────────────┤
│ Simples, mas     │ Maximiza         │ Menor overhead de         │
│ inflexível       │ throughput;      │ gerenciamento; risco de   │
│                  │ alto overhead    │ atraso se thread ocupada  │
└──────────────────┴──────────────────┴───────────────────────────┘
```

**Threads em clientes**: úteis para invocações concorrentes (ex.: navegador web buscando imagens em paralelo) e para desacoplar geração de dados da comunicação bloqueante.

### 7.3.6 Threads vs. Processos

| Critério | Thread (mesmo processo) | Novo processo |
|---|---|---|
| Criação | ~1 ms | ~11 ms |
| Troca de contexto | ~0,04–0,4 ms | ~1,8 ms |
| Compartilhamento de dados | Direto (memória compartilhada) | Requer IPC |
| Proteção mútua | Sem proteção entre threads | Protegidos pelo hardware |
| Falta de página inicial | Raro (cache quente) | Frequente (cache fria) |

### 7.3.7 Threads Java

```java
// Criar e iniciar uma thread
Thread t = new Thread(group, runnable, "nome");
t.setPriority(Thread.NORM_PRIORITY);
t.start();  // muda de SUSPENDED para RUNNABLE

// Sincronização com monitor
public synchronized void addTo(Queue q) {
    // seção crítica — no máximo uma thread por vez
    q.enqueue(item);
    q.notifyAll();  // acorda threads em wait()
}

public synchronized Object removeFrom(Queue q) {
    while (q.isEmpty()) q.wait();  // libera monitor e bloqueia
    return q.dequeue();
}
```

**Primitivas de sincronização Java**:

| Método | Efeito |
|---|---|
| `synchronized` | Define seção crítica (monitor) |
| `object.wait()` | Libera monitor e bloqueia thread |
| `object.notify()` | Acorda uma thread em wait() |
| `object.notifyAll()` | Acorda todas as threads em wait() |
| `thread.join()` | Bloqueia até a thread terminar |
| `thread.interrupt()` | Acorda prematuramente thread bloqueada |

### 7.3.8 Implementação de Threads

| Nível | Vantagens | Desvantagens |
|---|---|---|
| **Nível de núcleo** | Aproveita multiprocessador; falta de página bloqueia só a thread | Operações de thread mais caras (chamada de sistema) |
| **Nível de usuário** | Chaveamento sem chamada de sistema; escalonador customizável | Thread bloqueada bloqueia todo o processo; sem paralelismo real |
| **Híbrido (Solaris, Mach)** | Combina vantagens de ambos | Complexidade; thread em nível de núcleo bloqueada paralisa suas threads de usuário |

**Ativações do escalonador (FastThreads/Anderson)**:
- Núcleo aloca **processadores virtuais** a processos
- Núcleo notifica o escalonador em nível de usuário via **upcall** (ativação do escalonador — AE) sobre 4 eventos:
  - `processador virtual alocado` — nova fatia de tempo disponível
  - `AE bloqueio` — thread bloqueou no núcleo
  - `AE desbloqueio` — thread desbloqueada, pronta para rodar
  - `AE preempção` — processador retirado do processo

---

## 7.4 Comunicação e Invocação

### 7.4.1 Primitivas de Comunicação

Na prática, o middleware implementa RPC/RMI sobre **sockets TCP/UDP** (portabilidade, interoperabilidade). Núcleos especializados (Amoeba) oferecem primitivas de alto nível (`doOperation`, `getRequest`, `sendReply`), mas são menos portáveis.

**Composição dinâmica de protocolo**: pilha de protocolos se adapta dinamicamente (ex.: notebook usa Wi-Fi em trânsito, Ethernet no escritório) — suportada por Streams (UNIX), Horus, x-núcleo, CTP/Cactus.

### 7.4.2 Desempenho de Invocação

**Hierarquia de custos** (ordem crescente de latência):

```
Chamada de procedimento local: ~0,001 ms
Troca de contexto (mesma thread):  ~0,04 ms
Chamada de sistema (TRAP):         ~0,4 ms
RPC nula (rede local Ethernet):    ~0,1–1 ms
RPC via Internet:                  ~100–400 ms
```

**Componentes do atraso em uma RPC**:

| Componente | Descrição |
|---|---|
| Empacotamento (marshalling) | Serialização/desserialização de argumentos |
| Cópias de dados | Usuário → núcleo → protocolo → interface de rede (até 4 cópias) |
| Inicialização de pacotes | Construção de cabeçalhos + checksums |
| Escalonamento e troca de contexto | Chamadas de sistema, threads de servidor, gerenciador de rede |
| Espera por confirmações | Dependente do protocolo (TCP vs. UDP) |

**Gráfico latência × tamanho de dados**:
```
Atraso
  │    ╱──────────────────
  │   ╱  salto (novo pacote)
  │  ╱
  │ ╱  proporcional ao tamanho
  │╱
  └──────────────────────── Tamanho dos dados
    0      pacote_size
```

### 7.4.3 LRPC — Lightweight RPC

Otimização para RPC **dentro do mesmo computador** (caso mais frequente):

**Problema da RPC local padrão**: copia argumentos 4 vezes (stub cliente → buffer de núcleo → mensagem → stub servidor).

**Solução LRPC** (Bershad et al.):

```
Cliente           Núcleo           Servidor
  │                 │                 │
  │ 1. copia args  │                 │
  │ ──────────────►│                 │
  │ na pilha A     │ 2. ativa núcleo │
  │                │◄────────────────│
  │                │ 3. upcall       │
  │                │────────────────►│
  │                │ 4. exec + copia │
  │                │    resultados   │
  │◄───────────────│◄────────────────│
  │ 5. retorno     │                 │
```

- Argumentos copiados **1 vez** (na pilha A em região compartilhada)
- Thread do cliente *entra* no espaço de endereçamento do servidor (sem escalonar nova thread)
- **3× mais rápido** que RPC local convencional
- Transparente para o aplicativo (stub escolhe LRPC ou RPC em tempo de vinculação)

### 7.4.4 Operação Assíncrona

| Modelo | Descrição | Exemplo |
|---|---|---|
| **Invocações concorrentes** | Múltiplas threads fazem invocações bloqueantes em paralelo | Navegador buscando imagens |
| **Invocações assíncronas** | Chamada não bloqueante; resultado retornado via *promise* | Mercury (promise/claim/ready) |
| **Invocações assíncronas persistentes** | Enfileira requisições em log estável; reenvia indefinidamente | QRPC (Rover toolkit) para modo desconectado |

**QRPC (Queued RPC)** — para dispositivos móveis:
- Requisições armazenadas em log em disco enquanto desconectado
- Enviadas quando conectividade disponível (pode usar diferentes enlaces)
- Resultados armazenados na "caixa de correio" do cliente
- Priorização de invocações; decisão inteligente sobre qual enlace usar

---

## 7.5 Arquiteturas de Sistemas Operacionais

### 7.5.1 Núcleo Monolítico vs. Micronúcleo

```
Núcleo Monolítico                  Micronúcleo
┌──────────────────────┐           ┌───────────────────────────────┐
│ Sistema de arquivos  │           │ S1 │ S2 │ S3 │ S4  (servidores│
│ Rede (TCP/IP)        │           │    em nível de usuário)        │
│ Driver de disco      │           ├───────────────────────────────┤
│ Gerência de memória  │           │  Micronúcleo:                 │
│ Escalonador          │           │  - Espaços de endereçamento   │
│ (tudo no mesmo       │           │  - Threads                    │
│  espaço de end.)     │           │  - IPC local                  │
└──────────────────────┘           └───────────────────────────────┘
```

| Critério | Monolítico | Micronúcleo |
|---|---|---|
| Eficiência | Alta (sem cruzamento de espaços de end.) | Menor (invocações via IPC) |
| Extensibilidade | Baixa (difícil modificar) | Alta (módulos carregados dinamicamente) |
| Proteção modular | Fraca (mesmo espaço de end.) | Forte (espaços de end. separados) |
| Tamanho | Grande (megabytes) | Pequeno (menos sujeito a erros) |
| Exemplos | UNIX, Linux, Windows | Mach, Chorus, L4 |

**Estratégias mistas**:
- **SPIN**: único espaço de endereçamento + Modula-3 (tipo forte) + eventos para comunicação entre módulos
- **Nemesis**: núcleo + todos os módulos em único espaço de 64 bits; proteção por atributos de região
- **L4**: micronúcleo "segunda geração" — delega gerência de memória a servidores de usuário; otimiza IPC
- **Exonúcleo**: aloca recursos de baixíssimo nível (blocos de disco); todo restante implementado em bibliotecas de usuário

---

## 7.6 Virtualização em Nível de SO

### 7.6.1 Conceitos Fundamentais

**Virtualização**: múltiplas **máquinas virtuais (VMs)** sobre hardware físico, cada uma executando instância separada de SO.

**Monitor de máquina virtual (hipervisor)**: camada fina de software que multiplexa recursos físicos entre VMs.

| Tipo | Descrição | Vantagem | Desvantagem |
|---|---|---|---|
| **Virtualização completa** | Interface idêntica ao hardware | SO convidado sem modificação | Difícil em x86 (17 instruções sensíveis não privilegiadas) |
| **Paravirtualização** | Interface modificada | Melhor desempenho | SO convidado precisa ser portado |

**Condição de Popek & Goldberg** para virtualização:
> Uma arquitetura é virtualizável se **todas as instruções sensíveis são instruções privilegiadas** (podem ser capturadas pelo hipervisor).

No x86 isso **não vale** — 17 instruções sensíveis não são privilegiadas (ex.: `LAR`, `LSL`).

**Casos de uso da virtualização**:

| Caso | Benefício |
|---|---|
| Consolidação de servidores | Reduz hardware; facilita migração de VMs |
| Computação em nuvem (IaaS) | Aluga VMs para usuários (AWS, Azure) |
| Aplicações distribuídas dinâmicas | Cria/destrói VMs com pouca sobrecarga (jogos MMO) |
| Desktop com múltiplos SOs | Parallels, VirtualBox em um Mac/Linux |

### 7.6.2 Estudo de Caso: Xen

**Arquitetura Xen**:

```
┌────────────────────────────────────────────────────────────────┐
│  Domínio0 (XenoLinux)    │  DomínioU  │  DomínioU  │  ...     │
│  (plano de controle)     │ (convidado)│ (convidado)│          │
│  Drivers reais           │ drivers    │ drivers    │          │
│                          │ front-end  │ front-end  │          │
├──────────────────────────┴────────────┴────────────┴──────────┤
│                    Interface do Hipervisor                     │
│         CPU virtual │ Escalonamento │ Memória virtual         │
├────────────────────────────────────────────────────────────────┤
│                   Hardware físico (x86)                        │
└────────────────────────────────────────────────────────────────┘
```

**Conceitos chave**:

| Conceito | Descrição |
|---|---|
| **Domínio0** | VM privilegiada; drivers reais; plano de controle do Xen |
| **DomínioU** | VMs não privilegiadas; todo acesso via hipervisor |
| **Hiperchamada** | Substitui instrução privilegiada; capturada pelo hipervisor (assíncrona) |
| **VCPU** | CPU virtual; hipervisor escalona VCPUs nas CPUs físicas |

**Paravirtualização no x86 — anéis de privilégio**:

```
SO tradicional:          Xen (paravirtualização):
Anel 0: núcleo           Anel 0: hipervisor Xen
Anel 1: (não usado)      Anel 1: SO convidado
Anel 2: (não usado)      Anel 2: (não usado)
Anel 3: aplicativos      Anel 3: aplicativos
```

**Escalonadores do Xen**:

| Escalonador | Mecanismo | Uso |
|---|---|---|
| **SEDF** (Simple EDF) | VCPU com prazo (deadline) mais próximo executa primeiro; configurado por (n ms a cada m ms) | Tempo real suave |
| **Credit Scheduler** | Peso (weight) → cota da CPU; VCPUs *under* (com crédito) têm prioridade sobre VMs *over* | Cota proporcional, balanceamento de carga |

**Gerenciamento de memória — três níveis**:

```
Aplicativo        → memória virtual
SO convidado      → memória pseudofísica (espaço contíguo simulado)
Hipervisor        → memória física real (fragmentada)
```

Hiperchamada `pt_update(lista_de_requisições)`: SO convidado solicita atualizações em lote na tabela de páginas; hipervisor valida e aplica somente as seguras.

**Drivers de dispositivo divididos (split driver)**:

```
DomínioU (convidado)         Domínio0
  ┌──────────────┐             ┌──────────────────────┐
  │ Front-end    │◄──anel E/S─►│ Back-end             │
  │ (proxy)      │  (mem. comp.)│ (driver real Linux)  │
  └──────────────┘             └──────────┬───────────┘
                                           │
                                    Hardware físico
```

- **Back-end** (domain0): gerencia multiplexação; expõe interface genérica neutra ao SO convidado
- **Front-end** (domainU): proxy simples; comunica via anel de E/S em memória compartilhada
- **XenStore**: espaço de informações compartilhado para descoberta de dispositivos
- **XenBus**: conjunto de mecanismos de comunicação (anéis de E/S + eventos + XenStore)

**Para portar um SO ao Xen**:
1. Substituir instruções privilegiadas por hiperchamadas
2. Reimplementar instruções sensíveis não privilegiadas (preservando semântica)
3. Portar subsistema de memória virtual (memória pseudofísica)
4. Implementar drivers divididos (front-end) para cada dispositivo necessário

---

## Mapa Conceitual

```
Sistema Operacional em SD
├── Camada SO
│   ├── Encapsulamento
│   ├── Proteção (modo supervisor vs. usuário)
│   └── Concorrência
├── Processos e Threads
│   ├── Ambiente de execução
│   │   ├── Espaço de endereçamento
│   │   │   ├── Regiões
│   │   │   ├── Memória compartilhada
│   │   │   └── Copy-on-write
│   │   └── Recursos (sockets, semáforos)
│   └── Threads
│       ├── Arquiteturas de servidor
│       │   ├── Pool de trabalhadores
│       │   ├── Thread por pedido
│       │   ├── Thread por conexão
│       │   └── Thread por objeto
│       ├── Java threads (synchronized, wait, notify)
│       └── Implementação (núcleo, usuário, híbrida)
│           └── Ativações do escalonador
├── Comunicação e Invocação
│   ├── Sockets TCP/UDP (padrão)
│   ├── Desempenho de RPC
│   │   ├── Componentes do atraso
│   │   └── LRPC (1 cópia, sem nova thread)
│   └── Operação assíncrona
│       ├── Invocações concorrentes
│       ├── Promise/claim (Mercury)
│       └── QRPC (modo desconectado)
├── Arquiteturas de SO
│   ├── Monolítico (UNIX, Linux)
│   └── Micronúcleo (Mach, L4)
│       ├── SPIN (linguagem + eventos)
│       └── Exonúcleo (bibliotecas de usuário)
└── Virtualização
    ├── Virtualização completa
    ├── Paravirtualização
    └── Xen
        ├── Hipervisor (ring 0)
        ├── Domínio0 (controle + drivers reais)
        ├── DomínioU (convidados)
        ├── Hiperchamadas
        ├── Escalonadores (SEDF, Credit)
        ├── Memória pseudofísica
        └── Drivers divididos (split driver)
```

---

## Relevância para Sistemas de Informação

| Tópico do Capítulo | Aplicação em SI |
|---|---|
| **Multithreading em servidores** | Servidores de aplicação (JBoss, Tomcat) usam pool de threads para atender requisições HTTP concorrentes |
| **Balanceamento de carga / migração** | Kubernetes/Docker Swarm realocam containers entre nós com base em carga; análogo às políticas do capítulo |
| **Custos de RPC / LRPC** | Decisão de microserviços vs. monólito: chamadas entre microserviços têm custo maior que chamadas locais |
| **Invocações assíncronas (QRPC)** | Aplicativos móveis (apps offline-first) enfileiram requisições quando sem conexão — padrão em React Native, PWAs |
| **Copy-on-write** | Containers Docker usam copy-on-write em camadas de imagem; fork() eficiente em processos de servidor |
| **Virtualização / Xen** | IaaS (AWS EC2, Azure VMs) é diretamente baseado em hipervisores como Xen, KVM e VMware |
| **Computação em nuvem (IaaS/PaaS/SaaS)** | Fundamento de toda infraestrutura de TI corporativa moderna |
| **Micronúcleo vs. monolítico** | Linux (monolítico com módulos) vs. sistemas embarcados usando QNX (micronúcleo) — escolha arquitetural em IoT |
| **Domínio0 e isolamento de VMs** | Segurança em nuvem: isolamento entre VMs de clientes diferentes depende do hipervisor |

---

## Erros Conceituais Comuns

1. **"Threads são processos leves"** — threads *compartilham* o ambiente de execução do processo (sem proteção mútua); processos têm espaços de endereçamento isolados. A escolha depende da necessidade de proteção.

2. **"Mais threads = mais throughput"** — o ganho satura quando o gargalo muda (disco, rede, CPU). Exemplo: com cache 75% e bottleneck na CPU, 3+ threads não melhoram além de 400 req/s.

3. **"RPC sobre rede local é sempre mais lento que LRPC"** — LRPC só se aplica ao caso de dois processos no *mesmo computador*. Para nós diferentes, RPC via rede é a única opção.

4. **"Paravirtualização exige hardware especial"** — é uma técnica de *software*: o SO convidado é reescrito para usar hiperchamadas no lugar de instruções privilegiadas.

5. **"Micronúcleos são sempre melhores"** — micronúcleos pagam custo de IPC entre módulos. Núcleos monolíticos com boa engenharia de software (camadas, OO) podem ser igualmente extensíveis com melhor desempenho.

6. **"Virtualização completa no x86 funciona perfeitamente"** — x86 tem 17 instruções sensíveis que *não* são privilegiadas, violando a condição de Popek & Goldberg. Soluções: simulação total (lenta) ou paravirtualização (requer port do SO).

7. **"Copy-on-write duplica memória no fork()"** — o fork apenas marca páginas como somente leitura; a cópia física acontece *somente na primeira escrita*. Isso torna fork() eficiente mesmo com processos grandes.

---

## Questões de Revisão

1. Explique por que sistemas operacionais distribuídos (onde o SO gerencia todos os nós como um sistema único) não são amplamente adotados. Qual é a solução prática?

2. Qual a diferença entre **processo** e **thread**? Por que um servidor de banco de dados multithreaded tem melhor throughput do que um servidor com um único thread?

3. Descreva as quatro arquiteturas de servidor baseadas em threads (pool, por pedido, por conexão, por objeto). Qual é mais adequada para um servidor web com carga altamente variável?

4. Um servidor tem tempo médio de 5ms de processamento e 10ms de E/S por pedido. Calcule o throughput máximo para: (a) 1 thread; (b) N threads sem cache; (c) N threads com cache de 80% de acerto.

5. Quais são os principais componentes do atraso em uma chamada RPC? Por que o atraso da RPC nula é muito maior que o tempo de transmissão puro dos dados?

6. Explique o mecanismo LRPC. Por que ele é aproximadamente 3× mais rápido que a RPC local? Quando não faz sentido usá-lo?

7. Compare núcleos monolíticos e micronúcleos quanto a: eficiência, extensibilidade e proteção modular. Cite um exemplo real de cada tipo.

8. O que é a **condição de Popek & Goldberg** para virtualização? Por que ela *não* é satisfeita pela arquitetura x86, e como o Xen contorna esse problema?

9. Descreva a arquitetura do Xen: qual é o papel do Domínio0, do DomínioU, do hipervisor e das hiperchamadas?

10. Explique o modelo de **drivers de dispositivo divididos** no Xen. Qual é a função do front-end e do back-end? Como eles se comunicam?

---

## Referência

COULOURIS, G. et al. **Sistemas Distribuídos: Conceitos e Projeto**. 5. ed. Porto Alegre: Bookman, 2013. Capítulo 7 (p. 279–331).
