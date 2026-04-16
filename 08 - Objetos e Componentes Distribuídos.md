# Capítulo 8 — Objetos e Componentes Distribuídos
## Material Teórico para Sistemas Distribuídos

---

## Objetivos de Aprendizagem

Ao final deste capítulo, o aluno deverá ser capaz de:

1. Distinguir objetos distribuídos de objetos locais e identificar as complexidades adicionais
2. Descrever a arquitetura CORBA: ORB, POA, repositórios, IDL e IOR
3. Escrever interfaces IDL CORBA com módulos, métodos in/out, exceções e herança
4. Explicar os quatro problemas do middleware orientado a objetos que motivaram componentes
5. Definir componente de software (Szyperski) e diferenciar interfaces fornecidas de exigidas
6. Descrever o padrão contêiner e seu papel como servidor de aplicação
7. Comparar EJB e Fractal quanto a modelo de programação, peso e casos de uso

---

## Pré-requisitos Recomendados

- Capítulo 5 (RPC/RMI): stubs, proxies, referências de objeto remoto, IDL básica
- Programação orientada a objetos: interfaces, herança, encapsulamento
- Capítulo 6 (Comunicação Indireta): filas de mensagens, pub-sub (para beans baseados em mensagens)

---

## 8.1 Objetos Distribuídos

### 8.1.1 Contexto e Evolução

O middleware de objeto distribuído emergiu de três áreas convergentes:

| Origem | Contribuição |
|---|---|
| Sistemas distribuídos | Desejo por abstrações além do modelo cliente-servidor puro |
| Linguagens OO (Simula, Smalltalk, Java, C++) | Paradigma de programação consolidado e ferramental |
| Engenharia de software | UML como notação de projeto padronizada |

### 8.1.2 Objetos vs. Objetos Distribuídos

| Conceito local | Equivalente distribuído | Descrição |
|---|---|---|
| Referência de objeto | **Referência de objeto remoto** | Identificador globalmente único; pode ser passado como parâmetro |
| Interface | **Interface remota** | Especificada via IDL; abstrai métodos invocáveis remotamente |
| Ação | **Ação distribuída** | Iniciada por RMI; pode gerar cadeias de invocações |
| Exceção | **Exceção distribuída** | Inclui exceções extras: perda de mensagem, falha de processo |
| Coleta de lixo | **GC distribuído** | Objeto vivo enquanto houver *alguma* referência local ou remota |

### 8.1.3 Diferenças Importantes em Relação à OO Local

1. **Sem classe no middleware**: em ambientes heterogêneos (C++, Java, Python coexistindo), não há interpretação única de "classe". Usa-se **fábrica** (para criação) e **modelo** (para descrição de comportamento).

2. **Herança de interface, não de implementação**: middlewares distribuídos suportam apenas herança de interface (novas assinaturas de método). Herança de implementação é problemática em sistemas heterogêneos e de grande escala.

### 8.1.4 Complexidades Adicionais do Middleware Distribuído

| Aspecto | Descrição |
|---|---|
| Comunicação | RMI como mecanismo primário; frequentemente complementado por eventos distribuídos |
| Ciclo de vida | Criação, migração e exclusão de objetos no ambiente distribuído |
| Ativação/desativação | Objetos não podem estar ativos o tempo todo; ativação sob demanda é essencial |
| Persistência | Estado do objeto deve sobreviver a ciclos de ativação e falhas |
| Serviços adicionais | Nomes, segurança, transações — necessários para aplicações robustas |

---

## 8.2 Estudo de Caso: CORBA

### 8.2.1 Visão Geral

O **CORBA** (Common Object Request Broker Architecture) é um padrão do OMG para RMI multilinguagem. Componentes-chave:

```
┌──────────────────────────────────────────────────────────────────┐
│                    Arquitetura CORBA                             │
│                                                                  │
│  Cliente            Núcleo ORB            Servidor               │
│  ┌────────┐        ┌─────────┐         ┌──────────┐             │
│  │ Proxy  │◄──────►│  ORB    │◄───────►│ Esqueleto│             │
│  │(Stub)  │  IIOP  │ Núcleo  │  IIOP   │  (POA)   │             │
│  └────────┘        └────┬────┘         └────┬─────┘             │
│                         │                   │                    │
│              ┌──────────┴───────────┐        │                   │
│              │ Reposi-  │ Reposi-   │    ┌───┴──────────┐        │
│              │ tório de │ tório de  │    │ Reposi-      │        │
│              │ Interfaces│Implemen- │    │ tório de     │        │
│              │           │  tações  │    │ Implementações│       │
│              └──────────┴───────────┘    └──────────────┘        │
└──────────────────────────────────────────────────────────────────┘
```

**ORB** (Object Request Broker): agente que localiza o objeto remoto, ativa-o se necessário e entrega a requisição.

### 8.2.2 IDL CORBA

A IDL (Interface Definition Language) é independente de linguagem de implementação.

**Exemplo completo:**

```idl
module Whiteboard {

  struct Rectangle {
    long width; long height; long x; long y;
  };

  struct GraphicalObject {
    string type;
    Rectangle enclosing;
    boolean isFilled;
  };

  interface Shape {
    long getVersion();
    GraphicalObject getAllState();   // retorna estado do objeto
  };

  typedef sequence <Shape, 100> All;  // sequência de até 100 referências

  interface ShapeList {
    exception FullException { };    // exceção definida pelo usuário
    Shape newShape(in GraphicalObject g) raises (FullException);
    All allShapes();
    long getVersion();
  };
};
```

**Direção de parâmetros**:

| Palavra-chave | Direção | Uso |
|---|---|---|
| `in` | cliente → servidor | Argumento de entrada |
| `out` | servidor → cliente | Resultado extra |
| `inout` | bidirecional | Raro; dado é passado e retornado modificado |

**Semântica de invocação**:
- **Padrão**: "no máximo uma vez" (at-most-once)
- `oneway`: semântica "talvez" (maybe); não bloqueia; sem parâmetros de retorno

**Tipos primitivos** (15 no total): `short`, `long`, `unsigned long`, `float`, `double`, `char`, `boolean`, `octet`, `any`, etc.

**Tipos construídos da IDL**:

| Tipo | Exemplo | Passagem |
|---|---|---|
| `sequence` | `sequence<Shape, 100>` | Por valor |
| `string` | `string name` | Por valor |
| `array` | `octet uniqueId[12]` | Por valor |
| `struct` | `struct GraphicalObject {...}` | Por valor (cópia) |
| `enum` | `enum Rand {Exp, Number, Name}` | Por valor |
| `union` | `union Exp switch (Rand) {...}` | Por valor |

**Herança de interface**:
```idl
interface A { };
interface B: A { };         // herança simples
interface Z: B, C { };      // herança múltipla (evitar nomes ambíguos com B::Q, C::Q)
```

**Atributos IDL** → geram automaticamente getter e setter:
```idl
readonly attribute string listname;  // apenas getter
attribute long count;                // getter + setter
```

**Mapeamento IDL → Java**:

| IDL | Java |
|---|---|
| `struct` | Classe Java (sem métodos) |
| `enum` | Classe Java com constantes |
| `sequence` / `array` | Vetor Java |
| `exception` | Classe Java com variáveis de instância |
| parâmetro `out` | Classe `Holder` (ex.: `PersonHolder`) |

### 8.2.3 Arquitetura CORBA — Componentes

**Núcleo ORB**: comunicação, conversão referência↔string, lista de argumentos para invocação dinâmica.

**POA — Adaptador de Objeto Portável** (Portable Object Adapter):
- Liga objetos CORBA (IDL) a serventes (implementações na linguagem do servidor)
- Cria referências de objeto remoto (IOR)
- Ativa e desativa serventes sob demanda
- Políticas configuráveis: thread por invocação, referências transientes/persistentes, servente único ou por objeto

**Repositório de Implementações**:
- Mapeia: `nome do adaptador` → `caminho da implementação` + `hostname:porta`
- Ativa servidores sob demanda (objetos com IOR persistente)

**Repositório de Interfaces**:
- Fornece reflexão: dado um objeto remoto, permite descobrir seus métodos e tipos de parâmetro
- Usado com invocação dinâmica; não exigido para uso estático com proxies

**Invocação Dinâmica (DII)**: cliente sem proxy em tempo de compilação consulta o Repositório de Interfaces e constrói a chamada em tempo de execução.

**Esqueletos Dinâmicos (DSI)**: servidor aceita invocações para interfaces desconhecidas em tempo de compilação; inspeciona a requisição para descobrir objeto e método.

### 8.2.4 IOR — Referências de Objeto Interoperáveis

```
┌──────────────────────────────────────────────────────────────────┐
│                    Formato IOR                                   │
├──────────────────┬──────────────────────────┬───────────────────┤
│ ID de tipo IDL   │ Protocolo + Endereço      │ Chave de objeto   │
│ (identificador   │ IIOP: host + porta        │ nome do adaptador │
│  do repositório) │                           │ + nome do objeto  │
└──────────────────┴──────────────────────────┴───────────────────┘
```

| Tipo de IOR | Duração | Aponta para |
|---|---|---|
| **Transiente** | Vida do processo servidor | Servidor diretamente (host + porta) |
| **Persistente** | Entre instanciações | Repositório de implementações |

### 8.2.5 Serviços CORBA

| Serviço | Função |
|---|---|
| **Serviço de nomes** | Mapeia nomes → referências de objeto remoto (veja Cap. 9) |
| **Serviço de negócio (Trading)** | Localiza objetos por atributo (diretório) |
| **Serviço de evento** | Pub-sub via RMI CORBA |
| **Serviço de notificação** | Amplia eventos com filtros, confiabilidade e ordenação |
| **Serviço de segurança** | Autenticação, controle de acesso, comunicação segura, auditoria |
| **Serviço de transação** | Transações planas e aninhadas (Cap. 16-17) |
| **Serviço de controle de concorrência** | Travas para acesso concorrente a objetos |
| **Serviço de estado persistente** | Repositório de objetos persistentes |
| **Serviço de ciclo de vida** | Criar, excluir, copiar, mover objetos via fábricas |

### 8.2.6 Exemplo Cliente-Servidor CORBA em Java

**Servidor**:
```java
// ShapeListServant.java — classe servente
class ShapeListServant extends ShapeListPOA {
    private POA theRootpoa;

    public Shape newShape(GraphicalObject g)
            throws ShapeListPackage.FullException {
        ShapeServant shapeRef = new ShapeServant(g, version++);
        // registra o objeto no POA → obtém IOR
        org.omg.CORBA.Object ref = theRootpoa.servant_to_reference(shapeRef);
        return ShapeHelper.narrow(ref);  // narrow: converte Object → Shape
    }
}

// ShapeListServer.java — inicialização
public class ShapeListServer {
    public static void main(String args[]) {
        ORB orb = ORB.init(args, null);                              // 1. inicia ORB
        POA rootpoa = POAHelper.narrow(
            orb.resolve_initial_references("RootPOA"));              // 2. obtém POA raiz
        rootpoa.the_POAManager().activate();                         // 3. ativa POA
        ShapeListServant servant = new ShapeListServant(rootpoa);    // 4. cria servente
        org.omg.CORBA.Object ref = rootpoa.servant_to_reference(servant); // 5. registra no POA
        ShapeList SLRef = ShapeListHelper.narrow(ref);
        // 6. registra no Serviço de Nomes
        NamingContext nc = NamingContextHelper.narrow(
            orb.resolve_initial_references("NameService"));
        nc.rebind(new NameComponent[]{new NameComponent("ShapeList","")}, SLRef);
        orb.run();                                                   // 10. aguarda chamadas
    }
}
```

**Cliente**:
```java
public class ShapeListClient {
    public static void main(String args[]) {
        ORB orb = ORB.init(args, null);
        NamingContext nc = NamingContextHelper.narrow(
            orb.resolve_initial_references("NameService"));
        // resolve pelo nome → IOR → proxy local
        ShapeList shapeListRef = ShapeListHelper.narrow(
            nc.resolve(new NameComponent[]{new NameComponent("ShapeList","")}));
        Shape[] sList = shapeListRef.allShapes();      // invocação remota
        GraphicalObject g = sList[0].getAllState();     // encadeamento de invocações
    }
}
```

**Callbacks no CORBA**:
```idl
interface WhiteboardCallback {
    oneway void callback(in int version);  // oneway: assíncrono, sem bloqueio
};
interface ShapeList {
    int  register(in WhiteboardCallback callback);
    void deregister(in int callbackId);
};
```

---

## 8.3 De Objetos a Componentes

### 8.3.1 Problemas do Middleware Orientado a Objetos

Quatro limitações identificadas que motivaram a transição para componentes:

| Problema | Descrição | Requisito derivado |
|---|---|---|
| **Dependências implícitas** | Objetos chamam outros objetos/serviços internamente sem expor isso na interface | Tornar *todas* as dependências explícitas no contrato |
| **Interação com o middleware** | Código da aplicação misturado com chamadas ao POA, ORB, serviços (boilerplate) | Separação de preocupações: lógica de negócio vs. infraestrutura |
| **Sem separação de aspectos não funcionais** | Programador gerencia manualmente segurança, transações, etc. | Aspectos não funcionais gerenciados de forma transparente pelo middleware |
| **Sem suporte para implantação** | Objetos distribuídos manualmente; sem ferramental de deploy padronizado | Middleware com suporte intrínseco a implantação (deployment) |

### 8.3.2 Definição de Componente

> **Componente** (Szyperski): "uma unidade de composição com interfaces especificadas por contratos e **somente** dependências contextuais explícitas."

Um componente especifica:
- **Interfaces fornecidas** (*provided interfaces*): serviços que o componente oferece
- **Interfaces exigidas** (*required interfaces*): dependências de outros componentes

```
┌───────────────────────────────────────────────────────┐
│              Arquitetura de Software                  │
│                                                       │
│  [Módulo de bloco]──►[Módulo de dispositivo]          │
│         │                    │                        │
│         ▼                    ▼                        │
│  [Serviço de arquivo plano]──►[Serviço de diretório]  │
│                │                                      │
│                ▼                                      │
│         [Serviço de arquivos] ──► (interface fornecida│
│                                    para usuários)     │
│                                                       │
│  Legenda: ──► = interface exigida                     │
│           [X] = componente                            │
└───────────────────────────────────────────────────────┘
```

**Arquitetura de software** = componentes + interfaces + conexões entre interfaces.

### 8.3.3 Contêineres e Servidores de Aplicação

**Contêiner**: ambiente hospedeiro no servidor que:
1. Encapsula componentes e intercepta invocações recebidas
2. Gerencia propriedades não funcionais de forma transparente (transações, segurança, persistência)
3. Oculta toda interação com o middleware subjacente (ORB, POA)

```
┌────────────────────────────────────────────┐
│                  Contêiner                 │
│  ┌──────────────────────────────────────┐  │
│  │    Interceptação (aspecto externo)   │  │
│  │                                      │  │
│  │  ┌──────────┐     ┌──────────┐       │  │
│  │  │Componente│     │Componente│       │  │
│  │  │    A     │     │    B     │       │  │
│  │  └──────────┘     └──────────┘       │  │
│  └──────────────────────────────────────┘  │
│  Chamadas implícitas para serviços SD      │
│  (transação, segurança, nomes...)          │
└────────────────────────────────────────────┘
```

**Servidor de aplicação**: middleware que implementa o padrão contêiner. Exemplos:

| Servidor | Organização |
|---|---|
| WebSphere Application Server | IBM |
| Enterprise JavaBeans (EJB) | Sun/Oracle |
| JBoss | JBoss Community |
| Spring Framework | SpringSource/VMware |
| GlassFish | Sun/Oracle |

**Descritores de implantação**: arquivos XML que descrevem componentes, suas conexões e configurações de middleware (protocolo, POA, transações, segurança).

---

## 8.4 Estudos de Caso: EJB e Fractal

### 8.4.1 Enterprise JavaBeans (EJB 3.0)

**Contexto**: componente pesado para aplicações de três camadas (cliente → servidor de aplicação → banco de dados). Ideal para e-commerce, sistemas financeiros, ERPs.

**Papéis na especificação EJB**:

| Papel | Responsabilidade |
|---|---|
| Provedor de bean | Desenvolve a lógica da aplicação (POJO + anotações) |
| Montador de aplicação | Compõe beans em configurações de aplicação |
| Distribuidor | Implanta a configuração no ambiente operacional |
| Provedor de serviço | Define nível de suporte a transações, segurança |
| Provedor de persistência | Mapeia dados persistentes nos bancos de dados |
| Provedor de contêiner | Configura contêineres com os serviços exigidos |
| Administrador de sistema | Monitora e ajusta a implantação em execução |

**Tipos de bean EJB 3.0**:

| Tipo | Anotação | Características |
|---|---|---|
| Bean de sessão **com estado** | `@Stateful` | Mantém estado da conversa com um cliente específico |
| Bean de sessão **sem estado** | `@Stateless` | Sem estado; pode servir múltiplos clientes concorrentemente |
| Bean **baseado em mensagens** | `@MessageDriven` | Recebe mensagens via JMS (fila ou tópico); sem bloqueio do cliente |

**POJOs + Anotações** — modelo de programação simplificado:
```java
// Bean de sessão com estado — loja eletrônica
@Stateful
@TransactionManagement(CONTAINER)  // transações gerenciadas pelo contêiner
public class eShop implements Orders {

    @Resource javax.transaction.UserTransaction ut;  // injeção de dependência

    @TransactionAttribute(REQUIRED)   // política de transação declarativa
    public void MakeOrder(...) {
        // apenas lógica de negócio — contêiner gerencia o restante
    }

    @AroundInvoke   // interceptador de método (log de auditoria)
    public Object log(InvocationContext ctx) throws Exception {
        System.out.println("Método invocado: " + ctx.getMethod().getName());
        return ctx.proceed();   // continua execução normal
    }

    @PreDestroy     // interceptador de ciclo de vida
    void TidyUp() {
        // libera recursos antes de destruir o bean
    }
}
```

**Políticas de gerenciamento de transação**:

| Atributo | Política |
|---|---|
| `REQUIRED` | Usa transação existente do cliente ou inicia nova |
| `REQUIRES_NEW` | Sempre inicia nova transação |
| `SUPPORTS` | Usa transação do cliente se existir; sem transação caso contrário |
| `NOT_SUPPORTED` | Suspende transação do cliente durante a chamada |
| `MANDATORY` | Exige transação do cliente; dispara exceção se não houver |
| `NEVER` | Proíbe transação do cliente; dispara exceção se houver |

**Injeção de dependência**: contêiner resolve dependências declaradas com `@Resource`, `@EJB`, etc., em tempo de execução via reflexão.

**Interceptação**:

| Mecanismo | Anotação | Uso |
|---|---|---|
| Interceptar chamada de método | `@AroundInvoke` | Log, auditoria, controle de acesso |
| Após criação do bean | `@PostConstruct` | Inicialização de recursos |
| Antes de destruição | `@PreDestroy` | Liberação de recursos, escrita em BD |
| Após ativação (bean com estado) | `@PostActivate` | Restaurar estado passivado |
| Antes de passivação | `@PrePassivate` | Salvar estado no BD |

**InvocationContext** (contexto disponível no interceptador):

| Método | Retorna |
|---|---|
| `getTarget()` | Instância do bean interceptado |
| `getMethod()` | Método sendo invocado |
| `getParameters()` | Parâmetros da invocação |
| `setParameters()` | Altera parâmetros antes da execução |
| `proceed()` | Continua para o próximo interceptador ou para o método |

### 8.4.2 Fractal

**Contexto**: modelo de componente leve, linguagem-agnóstico, para construção de plataformas de middleware e sistemas configuráveis em tempo de execução.

**Implementações**: Julia/AOKell (Java), Cecilia/Think (C), FracNet (.NET), FracTalk (Smalltalk), Julio (Python).

**Interfaces no Fractal**:

| Tipo | Equivalente | Descrição |
|---|---|---|
| Interface de **servidor** | Interface fornecida | Aceita invocações recebidas |
| Interface de **cliente** | Interface exigida | Origina invocações enviadas |

**Vínculos (bindings)**:

| Tipo | Descrição | Implementação |
|---|---|---|
| **Primitivo** | Mapeamento direto interface cliente → interface servidor (mesmo espaço de endereçamento) | Referência direta (eficiente) |
| **Composto** | Arquitetura complexa entre múltiplos componentes, potencialmente em máquinas diferentes | É um componente Fractal — configurável e reconfigurável |

**Fractal ADL** (Architectural Description Language — XML-based):
```xml
<definition name="cs.ClientServer">
  <interface name="r" role="server" signature="java.lang.Runnable" />
  <component name="caller" definition="hw.CallerImpl" />
  <component name="callee" definition="hw.CalleeImpl" />
  <binding client="this.r"   server="caller.r" />
  <binding client="caller.s" server="callee.s" />
</definition>
```

Resultado:
```
cs.ClientServer
  r (servidor)
  ├── caller ──[s]──► callee
  └── (r de this vinculado a r de caller)
```

**Estrutura de um componente Fractal**:

```
┌──────────────────────────────────────────────┐
│                 Membrana                     │
│  Interfaces de cliente                       │
│  ┌───────────────────────────────────────┐   │
│  │         Controladores                │   │
│  │  (LifeCycleController, Component,    │   │
│  │   ContentController, Interceptação)  │   │
│  ├───────────────────────────────────────┤   │
│  │         Conteúdo                     │   │
│  │  (subcomponentes + vínculos)         │   │
│  └───────────────────────────────────────┘   │
│  Interfaces de servidor                      │
└──────────────────────────────────────────────┘
```

**Controladores principais**:

| Controlador | Interface | Métodos chave |
|---|---|---|
| **LifeCycleController** | Ciclo de vida | `startFc()`, `stopFc()`, `getFcState()` |
| **Component** | Reflexão / introspecção | `getFcInterfaces()`, `getFcInterface(name)`, `getFcType()` |
| **ContentController** | Composição | `getFcSubComponents()`, `addFcSubComponent(c)`, `removeFcSubComponent(c)` |
| **Interceptação** | Transparência | Intercepta invocações (log, segurança) |

```java
// Interface Component — introspecção
public interface Component {
    Object[] getFcInterfaces();
    Object   getFcInterface(String itfName);
    Type     getFcType();
}

// Interface ContentController — gerenciamento de subcomponentes
public interface ContentController {
    Object[]    getFcInternalInterfaces();
    Component[] getFcSubComponents();
    void        addFcSubComponent(Component c);
    void        removeFcSubComponent(Component c);
}
```

**Reconfiguração dinâmica**: suspender configuração (via LifeCycleController), substituir componente, retomar — tudo em tempo de execução sem reiniciar o sistema.

### 8.4.3 Comparação EJB vs. Fractal

| Critério | EJB 3.0 | Fractal |
|---|---|---|
| Peso | Pesado (servidor de aplicação completo) | Leve (mínimo, sem serviços integrados) |
| Linguagem | Java apenas | Agnóstico (Java, C, .NET, Python, Smalltalk) |
| Casos de uso | Aplicações 3 camadas, e-commerce, ERPs | Plataformas de middleware, sistemas configuráveis, IoT |
| Modelo de programação | POJO + anotações declarativas | ADL XML + interfaces de controlador |
| Gerenciamento não funcional | Gerenciado pelo contêiner (transações, segurança) | Via controladores configuráveis na membrana |
| Reconfiguração dinâmica | Limitada | Primeira classe (introspection + lifecycle) |
| Herança de configuração | Não aplicável | Hierárquica (componentes compostos) |
| Reflexão | Via anotações e CDI | ContentController + Component |
| Exemplos de uso | WebSphere, JBoss, GlassFish, Spring | Think (SO), DREAM (middleware), ProActive (Grid) |

### 8.4.4 Outros Modelos Leves

**OpenCOM**: modelo mínimo e independente de domínio; suporta carregamento/descarregamento dinâmico de componentes; overhead insignificante — adequado para roteadores e redes de sensores sem fio.

**OSGi**: especificação Java para bundles (pacotes modulares) com gerenciamento de ciclo de vida dinâmico (instalar, iniciar, parar, desinstalar, atualizar); serviços publicados em registro; vínculos dinâmicos. Usado em Eclipse (plug-ins), telefones móveis, computação em grade.

---

## Mapa Conceitual

```
Objetos e Componentes Distribuídos
├── Objetos Distribuídos
│   ├── Diferenças vs. OO local
│   │   ├── Referências remotas (IOR)
│   │   ├── Herança de interface (não de implementação)
│   │   └── Sem conceito de classe (heterogeneidade)
│   └── CORBA
│       ├── IDL: módulos, interfaces, métodos (in/out/inout/oneway), exceções, tipos
│       ├── Arquitetura: ORB núcleo, POA, esqueletos, stubs/proxies
│       ├── Repositórios: Interfaces + Implementações
│       ├── IOR: transiente vs. persistente
│       ├── Serviços CORBA: nomes, transação, segurança, eventos...
│       └── Invocação: estática (proxy/esqueleto) vs. dinâmica (DII/DSI)
├── Limitações do Middleware OO
│   ├── Dependências implícitas
│   ├── Boilerplate / interação com middleware
│   ├── Aspecto não funcionais misturados
│   └── Sem suporte a implantação
├── Componentes (Szyperski)
│   ├── Interfaces fornecidas + exigidas
│   ├── Arquitetura de software explícita
│   └── Contêineres (separação de preocupações)
│       └── Servidores de aplicação (EJB, JBoss, Spring)
└── Estudos de Caso
    ├── EJB 3.0
    │   ├── POJOs + anotações (@Stateful, @Stateless, @MessageDriven)
    │   ├── Transações gerenciadas por contêiner/bean
    │   ├── Injeção de dependência (@Resource)
    │   └── Interceptação (@AroundInvoke, @PostConstruct, @PreDestroy)
    └── Fractal
        ├── Interfaces servidor/cliente
        ├── Vínculos primitivos e compostos
        ├── ADL XML para composição hierárquica
        └── Membrana + Controladores (LifeCycle, Component, ContentController)
```

---

## Relevância para Sistemas de Informação

| Tópico do Capítulo | Aplicação em SI |
|---|---|
| **CORBA / IDL** | Integração de sistemas heterogêneos em empresas com múltiplas linguagens; ERP que expõe serviços para clientes Java e C++ |
| **IOR transiente vs. persistente** | Referências a serviços em nuvem (persistentes) vs. sessões efêmeras (transientes) |
| **Serviços CORBA de transação** | Base conceitual para gerenciamento de transações em bancos, seguradoras e e-commerce |
| **Limitações de objetos distribuídos** | Justificativa de negócio para migrar de CORBA/RMI monolítico para microsserviços ou componentes |
| **EJB e servidores de aplicação** | Todo sistema Java EE corporativo (portais bancários, sistemas de RH, e-commerce) usa esse padrão |
| **Contêineres e injeção de dependência** | Spring e CDI (Jakarta EE) são evolução direta do EJB; padrão ubíquo no desenvolvimento Java |
| **Anotações declarativas** | Programação moderna: `@Transactional`, `@Secured`, `@Cacheable` no Spring — mesmo princípio do EJB |
| **Fractal / componentes leves** | Arquiteturas de microsserviços modulares; middleware para IoT (OpenCOM) e plug-ins de IDE (OSGi/Eclipse) |
| **Composição sobre herança** | Princípio fundamental em design patterns modernos (composição, injeção de dependência) |
| **Arquitetura 3 camadas** | Padrão dominante em SI: front-end web → servidor de aplicação (EJB/Spring) → banco de dados |

---

## Erros Conceituais Comuns

1. **"CORBA só funciona com Java"** — CORBA é multilinguagem por design. O IDL é mapeado para Java, C++, Python, etc. RMI Java é que é restrito ao Java.

2. **"POA e ORB são a mesma coisa"** — ORB gerencia comunicação (serialização, transporte). POA é responsável pelo ciclo de vida dos serventes e pelo mapeamento de nomes de objetos para suas implementações.

3. **"IOR persistente = objeto permanentemente ativo"** — IOR persistente significa que a referência sobrevive entre execuções do servidor, mas o objeto é ativado *sob demanda* pelo Repositório de Implementações.

4. **"Componentes = objetos com mais funcionalidades"** — A diferença essencial é que componentes têm **dependências explícitas** (interfaces exigidas visíveis no contrato). Objetos têm dependências implícitas (chamadas internas invisíveis).

5. **"EJB gerencia transações automaticamente sem configuração"** — O EJB usa política padrão `REQUIRED`, mas o desenvolvedor precisa entender e possivelmente ajustar as políticas via `@TransactionAttribute`. Sem entender o modelo, geram-se bugs de consistência.

6. **"Fractal é apenas para Java"** — Fractal é agnóstico de linguagem. Tem implementações em C (Cecilia), .NET (FracNet), Python (Julio), Smalltalk (FracTalk). O Julia/Java é apenas a implementação de referência.

7. **"Herança IDL é igual a herança Java"** — IDL suporta apenas herança de interface (assinaturas de método). Não existe herança de implementação. Uma interface IDL pode ter herança múltipla desde que não haja métodos com nomes repetidos.

---

## Questões de Revisão

1. Quais são as três áreas que convergiram para o surgimento de middleware de objeto distribuído? Por que o conceito de "classe" é problemático no CORBA?

2. Descreva a diferença entre parâmetros `in`, `out` e `inout` na IDL do CORBA. Como um parâmetro `out` é tratado em Java, onde os métodos só podem retornar um valor?

3. Qual a diferença entre uma IOR transiente e uma IOR persistente? Em que cenário cada uma é mais adequada?

4. Explique as quatro limitações do middleware orientado a objetos que motivaram o surgimento de componentes. Dê um exemplo concreto de cada limitação.

5. Na definição de Szyperski, o que significa "somente dependências contextuais explícitas"? Por que isso é importante para composição terceirizada?

6. O que é um contêiner no contexto de middleware de componentes? Como ele implementa a separação de preocupações entre lógica de aplicação e gerenciamento de sistemas distribuídos?

7. Compare beans de sessão com estado e sem estado no EJB. Em que cenário cada tipo é mais adequado? Que implicações têm para escalabilidade?

8. No EJB, qual a diferença entre transações gerenciadas por bean e por contêiner? Quando é vantajoso usar cada abordagem?

9. No Fractal, qual a diferença entre vínculos primitivos e vínculos compostos? Por que vínculos compostos serem componentes Fractal é uma característica importante?

10. Compare EJB e Fractal quanto a: peso, modelo de programação, suporte a reconfiguração dinâmica e casos de uso típicos. Em que cenários você escolheria um ou outro?

---

## Referência

COULOURIS, G. et al. **Sistemas Distribuídos: Conceitos e Projeto**. 5. ed. Porto Alegre: Bookman, 2013. Capítulo 8 (p. 335–380).
