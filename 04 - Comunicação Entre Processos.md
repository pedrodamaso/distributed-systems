# Capítulo 4 — Comunicação Entre Processos
## Material Teórico para Sistemas Distribuídos
**Referência:** Coulouris, G. et al. *Sistemas Distribuídos: Conceitos e Projeto*, 5ª ed. Bookman, 2013.

---

## Objetivos de Aprendizagem

Ao final deste capítulo, o estudante deverá ser capaz de:

- Utilizar as APIs de sockets (UDP e TCP) para comunicação entre processos em Java
- Diferenciar comunicação síncrona e assíncrona e suas implicações em SD
- Explicar os três principais mecanismos de representação externa de dados (CORBA CDR, Java Serialization, XML)
- Compreender o funcionamento do multicast IP e seus casos de uso
- Entender o conceito de redes de sobreposição (overlay networks) e sua motivação
- Descrever a arquitetura do MPI e suas variantes de operações de envio

---

## Pré-requisitos

- Pilha de protocolos TCP/IP (Cap. 3): UDP, TCP, endereçamento IP, portas
- Conceito de processo e concorrência (Cap. 2)
- Modelo cliente-servidor (Cap. 1 e 2)
- Programação orientada a objetos em Java (básico)

---

## 4.1 Introdução: Camadas de Comunicação

O capítulo está posicionado na **camada de primitivas de comunicação** do middleware de sistemas distribuídos:

```
┌─────────────────────────────────────────────┐
│         Aplicações e Serviços               │
├─────────────────────────────────────────────┤
│  Invocação remota / Comunicação indireta    │  ← Caps. 5 e 6
├─────────────────────────────────────────────┤
│  Sockets · Passagem de mensagens            │
│  Multicast · Redes de sobreposição          │  ← Cap. 4 (este capítulo)
├─────────────────────────────────────────────┤
│              UDP e TCP                      │  ← Cap. 3
└─────────────────────────────────────────────┘
```

**Conceito central:** IPC (Inter-Process Communication) define os blocos básicos sobre os quais os protocolos de nível de aplicação são construídos.

---

## 4.2 API para Protocolos Internet

### 4.2.1 Conceitos Fundamentais de Passagem de Mensagens

| Conceito | Descrição |
|----------|-----------|
| **Destino da mensagem** | Par (endereço IP, número de porta); porta é gerenciada pelo SO |
| **Porta** | Ponto de chegada de mensagens em um processo; vários remetentes → 1 porta |
| **Confiabilidade** | UDP: não confiável (falhas por omissão); TCP: confiável (retransmissões) |
| **Ordenamento** | UDP: sem garantia; TCP: mantém ordem de envio |
| **Bloqueio** | Send/receive podem ser bloqueantes (síncronos) ou não bloqueantes (assíncronos) |

---

### 4.2.2 Comunicação via UDP (DatagramSocket)

UDP é um serviço de passagem de mensagens **sem conexão** e **não confiável** — sofre de falhas por omissão mas sem penalidades de desempenho.

**Classes Java:**
- `DatagramSocket` — socket UDP para envio/recebimento
- `DatagramPacket` — encapsula dados + endereço de destino

**Cliente UDP — exemplo conceitual:**
```java
DatagramSocket socket = new DatagramSocket();
byte[] m = message.getBytes();
InetAddress aHost = InetAddress.getByName(hostname);
int serverPort = 6789;
DatagramPacket request = new DatagramPacket(m, m.length, aHost, serverPort);
socket.send(request);
// aguarda resposta
byte[] buffer = new byte[1000];
DatagramPacket reply = new DatagramPacket(buffer, buffer.length);
socket.receive(reply);
socket.close();
```

**Servidor UDP — exemplo conceitual:**
```java
DatagramSocket socket = new DatagramSocket(6789);
while (true) {
    byte[] buffer = new byte[1000];
    DatagramPacket request = new DatagramPacket(buffer, buffer.length);
    socket.receive(request);
    // processa requisição
    DatagramPacket reply = new DatagramPacket(
        request.getData(), request.getLength(),
        request.getAddress(), request.getPort());
    socket.send(reply);
}
```

---

### 4.2.3 Comunicação via TCP (ServerSocket/Socket)

TCP fornece um **canal bidirecional confiável e orientado a fluxo** entre pares de processos. Garante entrega e ordem, mas com maior latência e custo de armazenamento.

**Classes Java:**
- `ServerSocket` — servidor aguarda conexões
- `Socket` — estabelece conexão TCP (cliente e thread de servidor)

**Servidor TCP — estrutura com thread por conexão:**
```java
ServerSocket listenSocket = new ServerSocket(7896);
while (true) {
    Socket clientSocket = listenSocket.accept();     // bloqueia aguardando
    Connection c = new Connection(clientSocket);     // thread para cada cliente
}

class Connection extends Thread {
    Socket clientSocket;
    Connection(Socket aClientSocket) {
        clientSocket = aClientSocket;
        start();
    }
    public void run() {
        // lê do clientSocket.getInputStream()
        // escreve em clientSocket.getOutputStream()
        clientSocket.close();
    }
}
```

**Cliente TCP:**
```java
Socket s = new Socket(hostname, 7896);
DataInputStream in = new DataInputStream(s.getInputStream());
DataOutputStream out = new DataOutputStream(s.getOutputStream());
// envia e recebe via streams
s.close();
```

---

### 4.2.4 Comparativo UDP vs TCP

| Aspecto | UDP | TCP |
|---------|-----|-----|
| Conexão | Sem conexão | Orientado a conexão |
| Confiabilidade | Não confiável (omissões) | Confiável (retransmissões) |
| Ordem | Não garantida | Mantida |
| Modo | Datagramas | Fluxo de bytes |
| Overhead | Baixo | Alto (handshake, ACKs) |
| Uso típico | DNS, streaming, multicast | HTTP, FTP, RPC, RMI |

---

### 4.2.5 Comunicação Síncrona vs Assíncrona

| Tipo | Comportamento | Uso |
|------|--------------|-----|
| **Síncrona (bloqueante)** | Remetente bloqueia até recebimento/entrega | Simplicidade, fluxo natural |
| **Assíncrona (não bloqueante)** | Remetente continua imediatamente | Alto desempenho, paralelismo |

> **Compromisso:** comunicação síncrona simplifica o raciocínio sobre o programa, mas desperdiça ciclos de CPU enquanto aguarda. Comunicação assíncrona exige buffer e gerenciamento de estado.

---

## 4.3 Representação Externa de Dados e Empacotamento

**Problema:** processos em nós distintos podem ter arquiteturas diferentes (big-endian/little-endian, tamanhos de tipos), linguagens diferentes e formatos de objeto distintos.

**Solução:** representação canônica de dados para transmissão — processo de **marshalling** (serializar) e **unmarshalling** (desserializar).

---

### 4.3.1 CORBA CDR (Common Data Representation)

- Define representação para **15 tipos primitivos** (short, long, ushort, ulong, float, double, boolean, char, octet, any, string, enum, sequence, struct, union)
- Adota **endianness do remetente** — mais eficiente pois evita conversão desnecessária se ambos forem iguais
- Tipos compostos são decompostos em primitivos
- Receptores sabem os **tipos antecipadamente** (via IDL — Interface Definition Language) — não há informação de tipo no fluxo

**Exemplo de serialização de struct:**
```
struct Pessoa {
    string nome;   // "Pedro" = 5 bytes
    long  idade;   // 32 anos = 4 bytes
}
// Fluxo CDR: [tam_nome][n][o][m][e][padding][idade]
```

---

### 4.3.2 Serialização Java

- Objetos que implementam `java.io.Serializable` podem ser serializados
- O fluxo inclui **informações completas de tipo** — receptor pode reconstruir sem conhecimento prévio
- Usa **reflexão** em vez de IDL para inspecionar a estrutura do objeto
- Suporta **handles** (identificadores) para evitar duplicação quando o mesmo objeto é referenciado múltiplas vezes
- API: `ObjectOutputStream.writeObject()` / `ObjectInputStream.readObject()`

```java
// Serialização
ObjectOutputStream out = new ObjectOutputStream(socket.getOutputStream());
out.writeObject(meuObjeto);

// Desserialização
ObjectInputStream in = new ObjectInputStream(socket.getInputStream());
MinhaClasse obj = (MinhaClasse) in.readObject();
```

---

### 4.3.3 XML (eXtensible Markup Language)

- Representação textual autodescritiva — inclui metadados de tipo junto aos dados
- Suporta **namespaces** para evitar conflito de nomes entre vocabulários distintos
- Estrutura validada via **XML Schema** ou **DTD**
- Dados binários requerem codificação (ex: Base64) pois XML é texto Unicode
- Processado via DOM (árvore em memória), SAX (eventos) ou JAXB (mapeamento Java↔XML)

```xml
<Pessoa xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <nome xsd:type="xsd:string">Pedro</nome>
  <idade xsd:type="xsd:integer">32</idade>
</Pessoa>
```

---

### 4.3.4 Comparativo dos Três Estilos de Empacotamento

| Aspecto | CORBA CDR | Java Serialization | XML |
|---------|-----------|--------------------|-----|
| Tipos no fluxo | Não (usa IDL) | Sim (reflexão) | Sim (elementos/atributos) |
| Formato | Binário | Binário | Texto |
| Tamanho | Compacto | Médio | Verboso |
| Legibilidade | Não | Não | Sim |
| Multilinguagem | Sim (via IDL) | Só Java | Sim |
| Esquema | IDL | `implements Serializable` | XSD/DTD |

---

### 4.3.5 Referências de Objetos Remotos

Para identificar um objeto em um sistema distribuído de forma única e global:

```
┌───────────────┬──────────┬───────────┬─────────────┐
│  Endereço IP  │  Porta   │ Timestamp │ Nº do Objeto│
│   32 ou 128   │  32 bits │  32 bits  │   32 bits   │
│     bits      │          │ (criação) │             │
└───────────────┴──────────┴───────────┴─────────────┘
```

- **IP + Porta**: identifica o processo servidor
- **Timestamp**: identifica o momento de criação (distingue reinicializações)
- **Nº do objeto**: identifica o objeto dentro do processo

---

## 4.4 Multicast IP

### 4.4.1 Fundamentos

Multicast permite que **um processo envie uma mensagem para um grupo de processos** com uma única operação de envio — eficiente por não exigir cópias individuais.

| Aspecto | Descrição |
|---------|-----------|
| **Faixa de endereços** | Classe D: 224.0.0.0 a 239.255.255.255 |
| **Associação ao grupo** | Processo entra/sai dinamicamente |
| **Confiabilidade** | Mesma semântica do UDP (falhas por omissão) |
| **Escopo (TTL)** | Time-to-live limita quantos roteadores a mensagem atravessa |
| **Suporte** | Redes locais e Internet (IGMP para gerenciar membros) |

---

### 4.4.2 API MulticastSocket em Java

```java
// Ingressar em um grupo multicast
MulticastSocket socket = new MulticastSocket(PORTA);
InetAddress grupo = InetAddress.getByName("228.5.6.7");
socket.joinGroup(grupo);

// Receber mensagem
byte[] buffer = new byte[1000];
DatagramPacket msg = new DatagramPacket(buffer, buffer.length);
socket.receive(msg);   // bloqueia

// Enviar mensagem para o grupo
DatagramPacket pacote = new DatagramPacket(
    data, data.length, grupo, PORTA);
socket.send(pacote);

// Sair do grupo
socket.leaveGroup(grupo);
```

---

### 4.4.3 Casos de Uso do Multicast

| Caso de Uso | Requisito de Confiabilidade | Descrição |
|-------------|---------------------------|-----------|
| **Tolerância a falhas por servidores replicados** | Alta | Requisições enviadas a todas as réplicas; mesmo sem garantia de ordem é aceitável se idempotente |
| **Descoberta de servidores em rede espontânea** | Média | Requisições periódicas compensam perdas ocasionais; usado pelo Jini |
| **Melhor desempenho por dados replicados** | Dependente do método | Distribui dados replicados para múltiplos destinatários; depende da política de replicação |
| **Propagação de notificações de evento** | Baixa a Média | Anuncia existência de serviços (ex: serviços de pesquisa Jini) |

---

### 4.4.4 Limitações e Multicast Confiável

O multicast IP básico sofre de:
- **Mensagens perdidas**: nem todos os membros recebem a mensagem
- **Ordem inconsistente**: membros diferentes recebem mensagens em ordens diferentes

Requisitos mais estritos (tratados no Cap. 15):
- **Multicast confiável**: ou todos recebem ou nenhum recebe (semântica atômica)
- **Multicast totalmente ordenado**: todos os membros recebem todas as mensagens na mesma ordem

---

## 4.5 Virtualização de Redes: Redes de Sobreposição

### 4.5.1 Motivação

**Problema:** a Internet é um único substrato de rede compartilhado por aplicações muito diversas. Modificar os protocolos para atender a um aplicativo pode prejudicar outros. Como otimizar a rede para tipos específicos de aplicação sem alterar a infraestrutura subjacente?

**Solução:** redes de sobreposição (overlay networks).

---

### 4.5.2 Definição e Características

Uma **rede de sobreposição** é uma rede virtual com seus próprios nós, enlaces, esquemas de endereçamento, protocolos e algoritmos de roteamento, construída **sobre** uma rede já existente (como IP).

**Vantagens:**
- Permite novos serviços sem alterar a rede subjacente
- Estimula experimentação e personalização
- Várias sobreposições podem coexistir simultaneamente

**Desvantagens:**
- Nível extra de indireção → possível queda de desempenho
- Aumenta complexidade dos serviços de rede

---

### 4.5.3 Tipos de Redes de Sobreposição

| Motivação | Tipo | Descrição |
|-----------|------|-----------|
| Necessidades do aplicativo | **Tabelas de hashing distribuídas (DHT)** | Mapeamento chave→valor descentralizado em larga escala; roteamento baseado em chave, topologia em anel |
| Necessidades do aplicativo | **Compartilhamento P2P de arquivos** | Mecanismos personalizados de endereçamento e roteamento para descoberta cooperativa de arquivos |
| Necessidades do aplicativo | **Redes de distribuição de conteúdo (CDN)** | Replicação, cache e posicionamento para entrega de conteúdo web e streaming de vídeo |
| Estilo de rede | **Redes ad hoc sem fio** | Protocolos de roteamento customizados; esquemas proativos (topologia pré-construída) ou reativos (rotas sob demanda/inundação) |
| Estilo de rede | **Redes tolerantes a rompimento (DTN)** | Operação em ambientes hostis com falhas significativas e grandes atrasos |
| Recursos adicionais | **Multicast** | Acesso a multicast onde não há roteadores multicast (ex: MBone) |
| Recursos adicionais | **Resiliência** | Maior robustez e disponibilidade de caminhos |
| Recursos adicionais | **Segurança** | VPNs e outras redes com segurança aprimorada sobre IP |

---

### 4.5.4 Estudo de Caso: Skype

O Skype é uma rede de sobreposição P2P para **voz sobre IP (VoIP)** com mensagens instantâneas, videoconferência e integração com telefonia convencional.

**Arquitetura da sobreposição:**

```
         ┌──────────────────────┐
         │  Servidor de Login   │  (autenticação centralizada)
         └──────────┬───────────┘
                    │
        ┌───────────┴───────────┐
        │   Supernós (SN)       │  (hosts com recursos suficientes)
        │  SN ── SN ── SN       │  (endereço IP global, alta largura de banda)
        └───────────┬───────────┘
                    │
        ┌───────────┴───────────┐
        │  Hosts convencionais  │  (usuários finais)
        └───────────────────────┘
```

| Aspecto | Detalhe |
|---------|---------|
| **Supernós** | Hosts com recursos suficientes; selecionados por largura de banda, acessibilidade (IP global, sem NAT) e disponibilidade |
| **Autenticação** | Servidor de login centralizado e conhecido |
| **Cache de supernós** | Cada cliente mantém cache com ~7 supernós iniciais, expandindo para centenas |
| **Busca de usuário** | Orquestrada pelo supernó do cliente; ~8 supernós consultados; 3-4 segundos típico (5-6 s com NAT) |
| **Conexão de voz** | TCP para sinalização; UDP (preferido) ou TCP para streaming de áudio |
| **Contorno de firewall** | Usa nó intermediário via TCP quando UDP é bloqueado |

> **Lição arquitetural:** o Skype demonstra como funcionalidade avançada (VoIP em escala global) pode ser implementada de forma específica ao aplicativo, sem modificar a arquitetura básica da Internet.

---

## 4.6 Estudo de Caso: MPI (Message Passing Interface)

### 4.6.1 Contexto e Motivação

- Padrão criado em 1994 pelo **MPI Forum** para computação de alto desempenho (HPC)
- Reação contra a proliferação de estratégias proprietárias de passagem de mensagens
- Objetivo: manter simplicidade e eficiência, mas com **portabilidade** e interface padronizada
- Mais de **115 operações** — especificação abrangente de passagem de mensagens
- Implementado em bibliotecas para C++, Fortran e outros; independente de SO

---

### 4.6.2 Modelo Arquitetônico

```
Processo p                                    Processo q
   │                                              │
   │ MPI_Send(...)                                │
   ▼                                              ▼
┌──────────────┐   ──── rede ────►  ┌──────────────┐
│ Buffer MPI   │                   │ Buffer MPI   │
│ (remetente)  │                   │ (destinatário)│
└──────────────┘                   └──────────────┘
                                          │
                                   MPI_Recv(...)
```

- Buffers da biblioteca MPI nos dois lados gerenciam dados em trânsito
- Separa explicitamente **semântica síncrona/assíncrona** de **bloqueante/não bloqueante**

---

### 4.6.3 Operações send Selecionadas

| Categoria | Com Bloqueio | Sem Bloqueio |
|-----------|-------------|--------------|
| **Genérica** | `MPI_Send`: bloqueia até ser seguro reutilizar o buffer | `MPI_Isend`: retorna imediatamente; usa `MPI_Wait`/`MPI_Test` para verificar progresso |
| **Síncrona** | `MPI_Ssend`: bloqueia até a mensagem ser entregue no destinatário | `MPI_Issend`: retorna imediatamente; `MPI_Wait`/`MPI_Test` indicam entrega no destinatário |
| **Com buffer** | `MPI_Bsend`: copia no buffer MPI do remetente e retorna | `MPI_Ibsend`: retorna imediatamente; `MPI_Wait`/`MPI_Test` indicam cópia no buffer MPI |
| **Pronta** | `MPI_Rsend`: remetente declara que destinatário está pronto → otimiza implementação | `MPI_Irsend`: mesmo efeito, não bloqueante; **perigoso** se presunção for falsa |

> **Atenção:** `MPI_Rsend` é **perigosa** — falha se o destinatário não estiver pronto. Requer conhecimento prévio do estado do receptor.

---

### 4.6.4 Operações Adicionais do MPI

| Operação | Descrição |
|----------|-----------|
| `MPI_Recv` | Receive bloqueante |
| `MPI_Irecv` | Receive não bloqueante |
| `MPI_Wait` | Aguarda conclusão de operação não bloqueante |
| `MPI_Test` | Testa (sem bloquear) se operação não bloqueante concluiu |
| **Comunicação coletiva** | Operações entre múltiplos processos |
| `scatter` | Um para muitos (distribuir dados) |
| `gather` | Muitos para um (coletar dados) |
| `broadcast` | Um para todos |
| `reduce` | Todos para um com operação de redução |

---

## Mapa Conceitual do Capítulo

```
                    COMUNICAÇÃO ENTRE PROCESSOS
                              │
          ┌───────────────────┼────────────────────┐
          │                   │                    │
      API Socket          Representação        Multicast
      (Seção 4.2)       de Dados (4.3)          (4.4)
          │                   │                    │
    ┌─────┴─────┐      ┌──────┼──────┐         Grupo
    │           │      │      │      │           IP
   UDP         TCP   CDR    Java   XML          Classe D
(Datagrama)  (Fluxo)CORBA  Serial.         (224-239.x.x.x)
Não confiável Confiável Binário Reflexão  Texto     │
                       IDL    Serializ.  Namespace  ├─ Confiável (Cap.15)
                       sem tipos com tipos completos └─ Ordenado (Cap.15)
          │
    ┌─────┴──────────┐
    │                │
Redes de         MPI
Sobreposição   (Seção 4.6)
(Seção 4.5)        │
    │          Blocking/Non-blocking
    │          Síncrono/Assíncrono
    ├─ DHT          │
    ├─ P2P     MPI_Send/Ssend/
    ├─ CDN     Bsend/Rsend
    ├─ Ad hoc  + variantes Isend
    └─ Skype   + coletivas
```

---

## Relevância para Sistemas de Informação

| Área de SI | Conexão com o Capítulo 4 |
|------------|--------------------------|
| **Desenvolvimento de Sistemas** | Toda integração entre sistemas usa sockets ou protocolos sobre sockets (REST/HTTP, gRPC, WebSockets) — entender a base permite diagnosticar problemas |
| **Banco de Dados** | Drivers JDBC/ODBC comunicam-se via TCP; replicação e clustering de bancos usam multicast ou overlay para sincronização |
| **Engenharia de Software** | Microsserviços comunicam-se via IPC (sockets, mensageria); testes de integração precisam considerar falhas de rede (UDP vs TCP) |
| **Segurança da Informação** | Sockets mal configurados são vetores de ataque; VPNs são overlay networks de segurança |
| **Gestão de TI** | Sistemas de monitoramento distribuído (Prometheus, Nagios) usam sockets; multicast em redes corporativas |
| **Arquitetura de Sistemas** | Message brokers (Kafka, RabbitMQ) abstraem IPC; API Gateways usam TCP; CDNs são overlay networks |
| **Computação em Nuvem** | Serviços cloud são acessados via sockets (HTTPS/TCP); load balancers operam na camada de transporte |
| **Computação de Alto Desempenho** | MPI é o padrão para HPC/clusters; relevante para analytics massivos em SI |

---

## Erros Comuns e Confusões

| Erro | Confusão | Correção |
|------|----------|----------|
| "UDP é sempre pior que TCP" | UDP é inadequado para aplicações críticas | UDP é ideal para streaming, jogos, DNS — onde latência importa mais que confiabilidade |
| "Serialização Java funciona em qualquer linguagem" | Java serialization usa formato binário proprietário | Para interoperabilidade, usar JSON, XML ou Protocol Buffers |
| "Multicast é confiável" | O multicast IP básico usa semântica UDP | Multicast confiável requer protocolo adicional (Cap. 15) |
| "Overlay network é sinônimo de VPN" | VPN é apenas um tipo de overlay | Overlays incluem DHTs, P2P, CDNs, ad hoc networks, etc. |
| "MPI_Rsend é a operação mais rápida" | É potencialmente a mais rápida, mas muito perigosa | Só usar se houver garantia de que o destinatário está pronto |
| "CORBA CDR inclui os tipos no fluxo" | CDR não inclui tipos — presupõe conhecimento via IDL | Java Serialization e XML é que incluem informação de tipo |
| "TCP garante entrega imediata" | TCP garante entrega mas não velocidade | TCP introduz overhead de handshake, ACKs e retransmissões |

---

## Questões de Revisão

1. Qual a diferença entre uma porta e um socket? Por que um processo servidor cria um `ServerSocket` antes de um `Socket`?

2. Compare a comunicação síncrona e assíncrona em termos de complexidade de implementação, throughput e risco de perda de mensagem.

3. Por que o CORBA CDR adota o endianness do remetente em vez de definir um endianness único para toda a rede?

4. Explique o papel dos handles (identificadores) na serialização Java. O que acontece sem eles quando objetos compartilham referências?

5. Um sistema distribui cotações de ações em tempo real para 10.000 clientes. Por que multicast IP seria preferível a 10.000 unicasts? Quais limitações do multicast IP devem ser consideradas?

6. Defina rede de sobreposição. Quais são as três categorias de motivação para criá-la (conforme o livro)?

7. Na arquitetura do Skype, qual o papel dos supernós? Quais critérios determinam se um host se torna supernó?

8. Explique a diferença entre `MPI_Ssend` (bloqueante síncrono) e `MPI_Isend` (não bloqueante genérico). Em que cenário de HPC cada um seria preferível?

9. Por que `MPI_Rsend` é descrita como "perigosa"? Em que condições ela oferece vantagem de desempenho?

10. Compare os três estilos de empacotamento (CDR, Java Serialization, XML) quanto à verbosidade, multilinguagem e autodescritibilidade dos dados.

---

## Referência

> COULOURIS, G.; DOLLIMORE, J.; KINDBERG, T.; BLAIR, G. **Sistemas Distribuídos: Conceitos e Projeto**. 5. ed. Porto Alegre: Bookman, 2013. Capítulo 4, p. 145-183.
