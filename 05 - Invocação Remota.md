# Capítulo 5 — Invocação Remota
## Material Teórico para Sistemas Distribuídos
**Referência:** Coulouris, G. et al. *Sistemas Distribuídos: Conceitos e Projeto*, 5ª ed. Bookman, 2013.

---

## Objetivos de Aprendizagem

Ao final deste capítulo, o estudante deverá ser capaz de:

- Descrever o protocolo de requisição-resposta e suas três variantes (R, RR, RRA)
- Explicar as três semânticas de chamada RPC (talvez, pelo menos uma vez, no máximo uma vez)
- Implementar uma interface de serviço usando IDL do CORBA ou Java
- Distinguir RPC de RMI e identificar quando usar cada paradigma
- Compreender os componentes de uma implementação de RMI (proxy, esqueleto, despachante)
- Utilizar os fundamentos da RMI Java (interfaces Remote, RMIregistry, callbacks, coleta de lixo)

---

## Pré-requisitos

- IPC via sockets UDP e TCP (Cap. 4)
- Representação externa de dados: marshalling/unmarshalling (Cap. 4, Seção 4.3)
- Referências de objetos remotos (Cap. 4, Seção 4.3.4)
- Modelo cliente-servidor e paradigmas arquiteturais (Cap. 2)
- Programação orientada a objetos em Java (interfaces, herança, exceções, serialização)

---

## 5.1 Introdução: Posicionamento no Middleware

O capítulo trata da camada de **invocação remota** — abstrações construídas sobre as primitivas IPC do Cap. 4:

```
┌─────────────────────────────────────────────────┐
│            Aplicações e Serviços                │
├─────────────────────────────────────────────────┤
│  Invocação remota (Cap. 5) +                    │
│  Comunicação indireta (Cap. 6)                  │
├─────────────────────────────────────────────────┤
│  Sockets · Multicast · Overlay (Cap. 4)         │
├─────────────────────────────────────────────────┤
│                UDP e TCP                        │
└─────────────────────────────────────────────────┘
```

Os três paradigmas estudados — requisição-resposta, RPC e RMI — permitem comunicação **direta** entre entidades distribuídas.

---

## 5.2 Protocolos de Requisição-Resposta

### 5.2.1 Primitivas Básicas

O protocolo define três operações:

```java
// Usado pelo cliente para invocar operação remota
public byte[] doOperation(RemoteRef s, int operationId, byte[] arguments)

// Usado pelo servidor para ler requisições
public byte[] getRequest()

// Usado pelo servidor para enviar resposta
public void sendReply(byte[] reply, InetAddress clientHost, int clientPort)
```

**Fluxo:**
1. Cliente chama `doOperation` → bloqueia
2. Servidor chama `getRequest` → processa
3. Servidor chama `sendReply` → cliente desbloqueia

---

### 5.2.2 Estrutura da Mensagem

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `messageType` | int (0=Request, 1=Reply) | Tipo da mensagem |
| `requestId` | int | Identificador único (sequência crescente + IP/porta do remetente) |
| `remoteReference` | RemoteRef | Referência ao objeto/servidor remoto |
| `operationId` | int ou Method | Operação a ser invocada |
| `arguments` | byte[] | Argumentos empacotados |

> **Identificador único:** `requestId` + identificador do processo remetente → exclusividade global no SD.

---

### 5.2.3 Tolerância a Falhas no Protocolo

**Problema:** UDP sofre de falhas por omissão. Como lidar?

| Mecanismo | Descrição |
|-----------|-----------|
| **Timeout + Retransmissão** | `doOperation` reenvio após timeout; exceção se nenhuma resposta |
| **Filtragem de duplicatas** | Servidor descarta requisições com mesmo `requestId` já processado |
| **Histórico** | Armazena última resposta por cliente para retransmissão sem reexecução |
| **Idempotência** | Operações que podem ser reexecutadas sem efeito diferente dispensam histórico |

> **Operação idempotente:** pode ser executada N vezes com o mesmo efeito que 1 vez. Ex: `PUT` (idempotente), `POST`/`append` (não idempotente).

---

### 5.2.4 Variantes do Protocolo (R, RR, RRA)

| Protocolo | Mensagens | Uso |
|-----------|-----------|-----|
| **R** (Request) | Cliente → Servidor | Sem valor de retorno; sem confirmação; fire-and-forget |
| **RR** (Request-Reply) | Cliente ↔ Servidor | Padrão client-server; reply é confirmação implícita |
| **RRA** (Request-Reply-Acknowledge) | Cliente ↔ Servidor + ACK | Reply confirmado explicitamente; permite limpar histórico |

> **Otimização RRA:** ACK pode ir "de carona" (piggyback) na próxima requisição, economizando uma mensagem.

---

### 5.2.5 UDP vs TCP para Requisição-Resposta

| Critério | UDP | TCP |
|----------|-----|-----|
| Tamanho máximo da mensagem | ~8-64 KB | Ilimitado |
| Confiabilidade | Protocolo deve tratar | Garantida pelo TCP |
| Sobrecarga | Baixa | Alta (3-way handshake, ACKs, controle de fluxo) |
| Histórico | Necessário | Desnecessário |
| Retransmissão | Manual | Automática |
| Recomendado para | Mensagens pequenas e idempotentes (NFS) | Argumentos/resultados grandes (RMI Java) |

---

### 5.2.6 HTTP como Protocolo de Requisição-Resposta

O HTTP é o exemplo mais amplamente usado. Métodos principais:

| Método | Idempotente? | Descrição |
|--------|-------------|-----------|
| **GET** | Sim | Recupera recurso; argumentos no URL |
| **HEAD** | Sim | Como GET, mas só retorna cabeçalhos (metadados) |
| **PUT** | Sim | Armazena/substitui recurso no URL dado |
| **DELETE** | Sim | Remove recurso |
| **POST** | Não | Envia dados para processamento; amplia recurso |
| **OPTIONS** | Sim | Lista métodos disponíveis para o URL |
| **TRACE** | Sim | Eco da requisição (diagnóstico) |

**Estrutura da mensagem HTTP:**
```
Requisição: [Método] [URL] [HTTP/versão] [Cabeçalhos] [Corpo opcional]
Resposta:   [HTTP/versão] [Código de status] [Motivo] [Cabeçalhos] [Corpo]
```

**HTTP/1.1** introduziu **conexões persistentes**: a mesma conexão TCP é reutilizada para múltiplas trocas requisição-resposta, reduzindo custo de setup.

---

## 5.3 Chamada de Procedimento Remoto (RPC)

### 5.3.1 Conceito e Motivação

A RPC estende a abstração de **chamada de procedimento local** para ambientes distribuídos, ocultando do programador:
- Empacotamento/desempacotamento de parâmetros
- Troca de mensagens de rede
- Localização do servidor

**Objetivo:** transparência de acesso e localização — o cliente chama um procedimento remoto como se fosse local.

---

### 5.3.2 Programação com Interfaces e IDL

Em SD, a **interface de serviço** define os procedimentos disponíveis remotamente. Restrições em relação a módulos locais:

1. **Sem acesso direto a variáveis** — apenas via métodos/procedimentos
2. **Sem passagem por referência** — parâmetros são `in`, `out` ou `inout`
3. **Sem endereços de processo** — endereços locais não têm validade remota

**IDL (Interface Definition Language)** permite que clientes e servidores sejam escritos em linguagens diferentes:

```idl
// Exemplo de IDL CORBA
struct Person {
    string name;
    string place;
    long year;
};

interface PersonList {
    readonly attribute string listname;
    void addPerson(in Person p);           // parâmetro de entrada
    void getPerson(in string name, out Person p);  // in + out
    long number();
};
```

IDLs notáveis: **XDR da Sun** (para RPC), **IDL do CORBA** (para RMI), **WSDL** (para Serviços Web), **Protocol Buffers** (Google).

---

### 5.3.3 Semânticas de Chamada RPC

| Medida de tolerância | Semântica resultante | Garantia |
|---------------------|---------------------|---------|
| Sem retransmissão, sem filtragem | **Talvez** (*maybe*) | Pode executar 0 ou 1 vez; vulnerável a omissões e falhas |
| Com retransmissão, sem filtragem | **Pelo menos uma vez** (*at least once*) | Executa ≥1 vez; seguro apenas para operações idempotentes |
| Com retransmissão + filtragem + histórico | **No máximo uma vez** (*at most once*) | Executa 0 ou 1 vez; mesmo efeito que chamada local |

> **Regra prática:** use "pelo menos uma vez" para operações idempotentes (NFS). Use "no máximo uma vez" para operações não idempotentes (transações bancárias).

---

### 5.3.4 Implementação de RPC

```
Processo Cliente                    Processo Servidor
────────────────────────────────────────────────────
  Programa    Stub     Módulo     Módulo    Stub     Despachante   Procedimento
  Cliente     cliente  Comunic.   Comunic.  servidor              de serviço
      │          │         │          │        │           │            │
      │──chama──►│         │          │        │           │            │
      │          │─ empacota, envia ──►│        │           │            │
      │          │         │          │──seleciona──►│      │            │
      │          │         │          │        │──desempacota, chama ───►│
      │          │         │          │        │           │     executa │
      │          │◄─────── resposta ──│        │           │◄────────────│
      │◄desempacota │      │          │        │           │            │
```

**Componentes:**
- **Stub no cliente**: comporta-se como procedimento local; empacota args, envia, recebe, desempacota
- **Despachante**: seleciona o stub correto no servidor pelo `operationId`
- **Stub no servidor**: desempacota args, chama o procedimento real, empacota resultado
- **Compilador de interface**: gera stubs automaticamente a partir da IDL

---

### 5.3.5 Estudo de Caso: RPC da Sun (Sun RPC / ONC RPC)

| Aspecto | Detalhe |
|---------|---------|
| **Transporte** | UDP (≤8-64 KB) ou TCP |
| **Semântica** | Pelo menos uma vez |
| **IDL** | XDR (External Data Representation) |
| **Compilador** | `rpcgen` → gera stubs e despachante em C |
| **Identificação** | Número de programa + número de versão (sem nome textual) |
| **Parâmetros** | Apenas 1 parâmetro de entrada; 1 de saída |

**Vinculação (binding):** `portmapper` — serviço em porta conhecida em cada host; mapeia (programa, versão) → porta. Clientes consultam o portmapper para descobrir a porta do servidor.

**Autenticação suportada:** nenhuma, estilo UNIX (uid/gid), chave compartilhada, Kerberos.

---

## 5.4 Invocação a Método Remoto (RMI)

### 5.4.1 RMI vs RPC

| Aspecto | RPC | RMI |
|---------|-----|-----|
| Paradigma | Procedural | Orientado a objetos |
| Passagem de parâmetros | Apenas por valor (in/out) | Por valor **e** por referência remota |
| Identidade | Identificador de procedimento | Referência de objeto remoto (globalmente única) |
| Herança | Não aplicável | Suportada (interfaces podem herdar) |
| Coleta de lixo | Não aplicável | Distribuída (contagem de referência) |
| IDL | Necessária para multilinguagem | Java: usa a própria linguagem; CORBA: IDL |

---

### 5.4.2 Modelo de Objeto Distribuído

**Conceitos fundamentais:**

| Conceito | Definição |
|----------|-----------|
| **Objeto remoto** | Objeto cujos métodos podem ser invocados de outros processos |
| **Referência de objeto remoto** | Identificador globalmente único: IP + porta + timestamp + nº objeto (Cap. 4) |
| **Interface remota** | Especifica quais métodos do objeto remoto são invocáveis remotamente |
| **Invocação local** | Entre objetos no mesmo processo |
| **Invocação remota (RMI)** | Entre objetos em processos distintos (mesmo host ou hosts diferentes) |

```
Processo 1                           Processo 2
┌────────────────────────┐           ┌────────────────────────┐
│  A ──invocação local──►C           │  B (objeto remoto)     │
│  │                     │           │  ┌──────────────────┐  │
│  └──invocação remota───┼──────────►│  │ Interface Remota │  │
│                         │           │  │  m1, m2, m3     │  │
└────────────────────────┘           └─────────────────────── ┘
```

---

### 5.4.3 Implementação de RMI: Componentes

```
         Cliente                              Servidor
┌─────────────────────────┐    ┌──────────────────────────────────┐
│  Objeto A               │    │  Objeto remoto B                 │
│       │                 │    │       ▲                          │
│       ▼                 │    │       │                          │
│  [Proxy para B]         │    │  [Esqueleto e Despachante de B]  │
│       │                 │    │       │                          │
│  [Módulo de             │    │  [Módulo de                      │
│   comunicação]          │    │   comunicação]                   │
│  [Módulo de ref.        │    │  [Módulo de ref.                 │
│   remota]               │    │   remota]                        │
└─────────────┬───────────┘    └────────────┬─────────────────────┘
              │◄─────── requisição/resposta ─┘
```

| Componente | Localização | Função |
|------------|-------------|--------|
| **Proxy** | Cliente | Imita objeto local; empacota args → mensagem; desempacota resultado |
| **Despachante** | Servidor | Recebe mensagem e seleciona o esqueleto correto pelo `operationId` |
| **Esqueleto** | Servidor | Desempacota args, chama servente, empacota resultado/exceção |
| **Servente** | Servidor | Instância real da classe que implementa a interface remota |
| **Módulo de comunicação** | Ambos | Executa protocolo requisição-resposta; garante semântica (no máximo uma vez) |
| **Módulo de ref. remota** | Ambos | Tabela: referência remota ↔ referência local; cria/consulta proxies |

> **Geração automática:** proxy, despachante e esqueleto são gerados por compilador de interface (CORBA) ou por reflexão em tempo de execução (Java RMI moderno).

---

### 5.4.4 Ativação e Objetos Persistentes

| Estado | Descrição |
|--------|-----------|
| **Ativo** | Objeto disponível em processo em execução |
| **Passivo** | Objeto com implementação + estado empacotado em disco, aguardando demanda |
| **Ativação** | Criação de objeto ativo a partir do passivo; iniciada pelo ativador |
| **Objeto persistente** | Mantém estado entre invocações; gerenciado por repositório de objetos persistentes |

**Ativador:** serviço responsável por registrar objetos passivos, iniciar processos servidor e ativar objetos sob demanda.

---

### 5.4.5 Coleta de Lixo Distribuída (Java RMI)

Baseada em **contagem de referência** + **leasing**:

```
1. Cliente recebe ref. remota para B pela 1ª vez
   → Cliente chama addRef(B) no servidor
   → Servidor adiciona cliente em B.holders
   → Cliente cria proxy para B

2. Cliente deixa de usar B (proxy sem referência local)
   → Cliente chama removeRef(B) no servidor
   → Servidor remove cliente de B.holders
   → Proxy é excluído

3. B.holders vazio → coletor local recupera B
```

**Leasing:** cliente deve renovar periodicamente o leasing; se processo cliente falha sem chamar `removeRef`, o leasing expira e o servidor limpa automaticamente.

---

## 5.5 Estudo de Caso: RMI Java

### 5.5.1 Interfaces Remotas

Toda interface remota em Java:
1. Estende `java.rmi.Remote`
2. Todos os métodos declaram `throws RemoteException`

```java
import java.rmi.*;
import java.util.Vector;

public interface Shape extends Remote {
    int getVersion() throws RemoteException;
    GraphicalObject getAllState() throws RemoteException;    // retorno por valor
}

public interface ShapeList extends Remote {
    Shape newShape(GraphicalObject g) throws RemoteException; // retorna ref. remota
    Vector allShapes() throws RemoteException;
    int getVersion() throws RemoteException;
}
```

---

### 5.5.2 Passagem de Parâmetros na RMI Java

| Tipo de parâmetro | Mecanismo | Efeito |
|-------------------|-----------|--------|
| **Objeto remoto** (interface `Remote`) | Passado como **referência remota** | Receptor pode invocar métodos remotos no objeto original |
| **Objeto não remoto serializável** (`implements Serializable`) | Passado **por valor** (cópia serializada) | Receptor tem cópia independente; alterações locais não afetam original |
| **Tipos primitivos** | Por valor | Comportamento convencional |

> **Download de classes:** se o destino não tiver a classe de um objeto passado por valor, o bytecode é baixado automaticamente via URL anotada na serialização.

---

### 5.5.3 RMIregistry — O Vinculador

O `RMIregistry` é um serviço de nomes que mapeia strings (estilo URL) → referências de objeto remoto.

```java
// Classe Naming — interface para o RMIregistry

void rebind(String name, Remote obj)    // servidor registra (sobrescreve se existir)
void bind(String name, Remote obj)      // servidor registra (exceção se já existir)
void unbind(String name, Remote obj)    // remove vínculo
Remote lookup(String name)              // cliente busca referência remota
String[] list()                         // lista nomes registrados
```

**Formato do nome:** `//nomeComputador:porta/nomeObjeto`

---

### 5.5.4 Programa Servidor Típico

```java
import java.rmi.*;
import java.rmi.server.UnicastRemoteObject;

public class ShapeListServer {
    public static void main(String[] args) {
        System.setSecurityManager(new RMISecurityManager());
        try {
            ShapeList aShapeList = new ShapeListServant();          // 1. cria servente
            ShapeList stub = (ShapeList)
                UnicastRemoteObject.exportObject(aShapeList, 0);    // 2. exporta objeto
            Naming.rebind("//bruno.ShapeList", stub);               // 3. registra no RMIregistry
            System.out.println("ShapeList server ready");
        } catch (Exception e) { System.out.println(e.getMessage()); }
    }
}
```

**Servente (implementa a interface remota):**
```java
public class ShapeListServant implements ShapeList {
    private Vector theList;
    private int version;

    public Shape newShape(GraphicalObject g) {    // método de fábrica
        version++;
        Shape s = new ShapeServant(g, version);   // cria novo objeto remoto
        theList.addElement(s);
        return s;    // retornado como referência remota (Shape é interface Remote)
    }
    // ...
}
```

---

### 5.5.5 Programa Cliente Típico

```java
import java.rmi.*;
import java.util.Vector;

public class ShapeListClient {
    public static void main(String[] args) {
        System.setSecurityManager(new RMISecurityManager());
        try {
            ShapeList aShapeList =
                (ShapeList) Naming.lookup("//bruno.ShapeList");   // 1. obtém ref. remota
            Vector sList = aShapeList.allShapes();                 // 2. invoca método remoto
        } catch (RemoteException e) { System.out.println(e.getMessage()); }
    }
}
```

---

### 5.5.6 Callbacks

Callbacks invertem o papel: o **servidor notifica o cliente** em vez de o cliente consultar o servidor.

**Passos:**
1. Cliente cria objeto remoto que implementa interface de callback
2. Cliente registra esse objeto no servidor (`register(callback)`)
3. Quando evento ocorre, servidor chama `callback()` nos clientes registrados
4. Ao terminar, cliente desregistra (`deregister(callbackId)`)

```java
public interface WhiteboardCallback extends Remote {
    void callback(int version) throws RemoteException;
}

// Na interface ShapeList, adicionar:
int register(WhiteboardCallback callback) throws RemoteException;
void deregister(int callbackId) throws RemoteException;
```

**Vantagens vs polling:**
- Elimina consultas desnecessárias ao servidor
- Notificação imediata dos clientes

**Desvantagens:**
- Servidor mantém lista de callbacks; clientes que terminam sem deregistrar geram lixo → usar leasing

---

### 5.5.7 Implementação Interna: Reflexão

A partir do Java 1.2, o **despachante genérico** usa reflexão (`java.lang.reflect.Method`) — um único despachante serve para todas as classes de objeto remoto:

```java
// Proxy empacota na mensagem de requisição:
Method m = ...;             // objeto Method (nome + tipos de parâmetros + classe)
Object[] args = {...};      // argumentos

// Despachante no servidor desempacota e invoca:
Object result = aMethod.invoke(targetObject, argumentsArray);
```

**Hierarquia de classes:**
```
RemoteObject
    └── RemoteServer
            ├── UnicastRemoteObject  (objeto vive enquanto processo existir)
            └── Activatable          (objeto passível de ativação sob demanda)
```

---

## Mapa Conceitual do Capítulo

```
                        INVOCAÇÃO REMOTA
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
  Req.-Resposta             RPC                   RMI
  (Seção 5.2)           (Seção 5.3)           (Seção 5.4)
          │                    │                    │
  3 primitivas:         Programação         Modelo de Objeto
  doOperation           com interfaces      Distribuído
  getRequest                 │                    │
  sendReply             IDL: XDR/CORBA      Ref. Obj. Remota
          │             WSDL/Protobuf       Interface Remota
  3 variantes:               │              Proxy/Esqueleto
  R, RR, RRA           Semântica chamada:  Despachante/Servente
          │             Talvez                    │
  Modelo falhas:        ≥1 vez             Coleta de lixo
  Omissão + colapso     ≤1 vez             distribuída
  Idempotência               │             (addRef/removeRef
  Histórico            Sun RPC:            + leasing)
  Timeout              portmapper               │
                       rpcgen/XDR          Estudo de caso:
  HTTP (5.2.5):        Autenticação        RMI Java (5.5)
  GET/POST/PUT/...                         Remote + RMIregistry
  MIME types                               Callbacks
  HTTP/1.1 persistente                     Download de classes
```

---

## Relevância para Sistemas de Informação

| Área de SI | Conexão com o Capítulo 5 |
|------------|--------------------------|
| **Desenvolvimento de Sistemas** | Toda API REST é um protocolo requisição-resposta sobre HTTP; gRPC usa protocolo binário semelhante à RPC; microsserviços comunicam-se por RPC/RMI |
| **Banco de Dados** | Drivers JDBC usam protocolo semelhante à RPC para enviar queries; procedures armazenadas remotas são análogas à RPC |
| **Engenharia de Software** | IDLs (WSDL, OpenAPI/Swagger) são o equivalente atual das IDLs CORBA/XDR para especificar interfaces de serviço |
| **Arquitetura de Sistemas** | ORBs (Object Request Brokers), ESBs e API Gateways são implementações do padrão proxy/despachante; Feign Client em Spring implementa proxies RMI |
| **Segurança da Informação** | Autenticação na RPC da Sun (UNIX, Kerberos) é a base dos mecanismos de autenticação em APIs modernas; RMISecurityManager → gerenciadores de segurança atuais |
| **Gestão de TI** | SLAs de microsserviços dependem da semântica de chamada escolhida (idempotência, retentativas) |
| **Computação em Nuvem** | Lambdas/Functions-as-a-Service são objetos remotos ativados sob demanda; service mesh (Istio) implementa proxies transparentes |
| **Integração de Sistemas** | SOA (Service-Oriented Architecture) e integração ERP/CRM usam WSDL/SOAP — evolução direta da IDL e RPC |

---

## Erros Comuns e Confusões

| Erro | Confusão | Correção |
|------|----------|----------|
| "RMI e RPC são a mesma coisa" | São paradigmas relacionados mas distintos | RPC é procedural; RMI adiciona objetos, herança, referências remotas e GC distribuído |
| "Semântica 'pelo menos uma vez' é suficiente para qualquer serviço" | Pode causar efeitos duplicados em operações não idempotentes | Só é segura se todas as operações remotas forem idempotentes |
| "O proxy executa o método diretamente" | Parece um objeto local, mas não executa localmente | O proxy empacota a chamada, envia pela rede e aguarda resposta do servidor |
| "O esqueleto é desnecessário no Java moderno" | Java 1.2+ usa reflexão e despachante genérico, eliminando esqueletos compilados | Correto para RMI Java; CORBA ainda pode usar esqueletos estáticos |
| "Objetos remotos em Java são passados por referência" | Objetos **remotos** são passados como referência remota; objetos **não remotos** são copiados | A distinção é feita pelo fato de implementar ou não a interface `Remote` |
| "TCP garante semântica de invocação 'exatamente uma vez'" | TCP garante entrega da mensagem, não execução do procedimento | Se a conexão cai antes do ACK, o cliente não sabe se o servidor executou — ainda é "no máximo uma vez" |
| "RMIregistry substitui um servidor de nomes completo" | O RMIregistry é simples: só mapeia nomes locais | Para SD complexos, usar JNDI, CORBA Naming Service ou equivalente |

---

## Questões de Revisão

1. Por que a implementação de protocolos de requisição-resposta sobre UDP normalmente exige filtragem de duplicatas, enquanto a implementação sobre TCP não?

2. Explique o conceito de operação idempotente. Dê um exemplo de operação idempotente e um de não idempotente em um sistema bancário. Qual semântica de chamada RPC é adequada para cada caso?

3. Compare os protocolos RR e RRA quanto ao número de mensagens trocadas e à capacidade de limpar o histórico no servidor. Em que cenário RRA é claramente superior ao RR?

4. Qual é a diferença entre parâmetros `in`, `out` e `inout` em uma IDL? Por que a chamada por referência do C++ não pode ser usada diretamente em RPC?

5. Um cliente recebe uma exceção `RemoteException` em uma chamada RMI Java. Que informações a exceção fornece sobre se o procedimento remoto foi executado ou não?

6. Descreva as funções do proxy, do despachante e do esqueleto em uma implementação RMI. Qual é a vantagem de gerar esses componentes automaticamente a partir da IDL?

7. Na RMI Java, qual é a diferença entre passar um objeto que implementa `Serializable` e passar um objeto que implementa `Remote` como argumento de um método remoto?

8. Explique o mecanismo de coleta de lixo distribuída da RMI Java usando `addRef`/`removeRef` e leasing. Por que o leasing é necessário para tolerar falhas de processos clientes?

9. O que é um callback na RMI Java? Compare a estratégia de callback com a de polling (consulta periódica) em termos de desempenho do servidor e latência de notificação.

10. Considere um serviço de votação eletrônica com os métodos `vote(candidato, idVotante)` e `result()`. Qual semântica de chamada RPC você escolheria para o método `vote`? Justifique considerando as consequências de cada semântica.

---

## Referência

> COULOURIS, G.; DOLLIMORE, J.; KINDBERG, T.; BLAIR, G. **Sistemas Distribuídos: Conceitos e Projeto**. 5. ed. Porto Alegre: Bookman, 2013. Capítulo 5, p. 185-228.
