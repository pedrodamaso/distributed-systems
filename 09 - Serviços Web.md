# Capítulo 9 — Serviços Web
## Material Teórico para Sistemas Distribuídos

> **Livro-base:** Coulouris et al., *Sistemas Distribuídos: Conceitos e Projeto*, 5ª ed., Bookman, 2013  
> **Capítulo:** 9 — Web Services (pp. 381–422)

---

## Objetivos de Aprendizagem

Ao final deste capítulo, o aluno deverá ser capaz de:

1. Explicar o modelo de comunicação SOAP e sua estrutura de envelope XML
2. Comparar REST e SOAP como paradigmas de acesso a serviços Web
3. Descrever a estrutura de uma descrição WSDL (parte abstrata e concreta)
4. Explicar o papel do UDDI como registro de serviços
5. Diferenciar segurança de canal (TLS) e segurança de documento (XML Security)
6. Descrever os requisitos de coreografia de serviços Web e a função do WS-Coordination
7. Relacionar Serviços Web com SOA, computação em grade (Grid) e computação em nuvem

---

## Pré-requisitos

| Conceito | Onde revisar |
|---|---|
| RPC e comunicação cliente-servidor | Capítulo 5 |
| Middleware de objetos distribuídos (CORBA, EJB) | Capítulo 8 |
| Segurança: criptografia simétrica/assimétrica, certificados X.509 | Capítulo 11 |
| Virtualização e Xen | Capítulo 7 (Seção 7.7) |
| XML básico e HTTP | Conhecimento prévio |

---

## 1. Introdução aos Serviços Web

### 1.1 Motivação

Os serviços Web surgiram da necessidade de **interligação entre organizações diferentes** via Internet — o que o middleware convencional (CORBA, DCOM) não resolvia adequadamente por exigir plataformas compatíveis.

**Princípios fundamentais:**
- Uso de **HTTP** como transporte (ubíquo, atravessa firewalls)
- Uso de **URIs** para identificar recursos
- Uso de **XML** como formato de representação (textual, auto-descritivo, interoperável)
- **Baixo acoplamento**: clientes conhecem apenas a interface, não a implementação

### 1.2 Duas Origens dos Serviços Web

| Origem | Descrição |
|---|---|
| Extensão de servidores Web | Adicionar interfaces de serviço para que programas (além de navegadores) acessem recursos via HTTP |
| RPC sobre Internet | Fornecer chamadas remotas usando protocolos existentes (HTTP + XML), sem exigir middleware proprietário |

### 1.3 Comparação com Objetos Distribuídos

| Aspecto | Objetos Distribuídos (CORBA/Java RMI) | Serviços Web |
|---|---|---|
| Instanciação remota | Sim (factory de objetos) | Não |
| Servents | Sim | Não |
| Referências remotas como retorno | Sim | Não |
| Herança de interface | Sim | Não suportado |
| Acoplamento | Maior | Menor |
| Interoperabilidade Internet | Difícil | Nativa |

---

## 2. SOAP — Simple Object Access Protocol

### 2.1 Estrutura do Envelope SOAP

O envelope SOAP é um documento XML com duas partes:

```xml
<!-- Requisição: cliente → servidor -->
<env:Envelope xmlns:env="http://www.w3.org/2003/05/soap-envelope">
  <env:Header>
    <!-- Cabeçalhos opcionais: roteamento, autenticação, transação -->
    <m:reservation xmlns:m="http://travelservice.org/reservation"
                   env:role="http://www.w3.org/2003/05/soap-role/next"
                   env:mustUnderstand="true">
      <m:reference>uuid:093a2da1-q345-739r-ba5d-pqff98fe8j7d</m:reference>
    </m:reservation>
  </env:Header>
  <env:Body>
    <!-- Corpo obrigatório: payload da requisição -->
    <m:GetLastShape xmlns:m="http://ShapeService.org/ws">
      <m:shapeList>aShapeList</m:shapeList>
    </m:GetLastShape>
  </env:Body>
</env:Envelope>

<!-- Resposta: servidor → cliente -->
<env:Envelope xmlns:env="http://www.w3.org/2003/05/soap-envelope">
  <env:Body>
    <m:GetLastShapeResponse xmlns:m="http://ShapeService.org/ws">
      <m:shape>Circle</m:shape>
      <m:color>Red</m:color>
    </m:GetLastShapeResponse>
  </env:Body>
</env:Envelope>

<!-- Erro: elemento Fault no corpo -->
<env:Envelope>
  <env:Body>
    <env:Fault>
      <env:Code><env:Value>env:Sender</env:Value></env:Code>
      <env:Reason><env:Text>ShapeList is empty</env:Text></env:Reason>
    </env:Fault>
  </env:Body>
</env:Envelope>
```

### 2.2 Transporte HTTP

```
POST /ShapeService HTTP/1.1
Host: example.org
Content-Type: application/soap+xml; charset="utf-8"
Content-Length: nnnn
Action: "http://ShapeService.org/ws/getAllState"

[envelope SOAP aqui]
```

**Vantagem do HTTP:** Atravessa firewalls corporativos (porta 80/443) sem configuração adicional.

### 2.3 REST vs. SOAP

| Aspecto | SOAP | REST |
|---|---|---|
| Paradigma | RPC orientado a operações | Recursos identificados por URL |
| Verbos HTTP | Apenas POST | GET, PUT, DELETE, POST |
| Formato | XML obrigatório | JSON, XML, texto livre |
| Descoberta | WSDL | Documentação informal |
| Overhead | Alto (14× mensagens maiores) | Baixo |
| Uso Amazon | 20% das requisições | 80% das requisições |

**REST:** `GET /shapes/123` → recupera recurso  
**REST:** `DELETE /shapes/123` → remove recurso  
**REST:** `PUT /shapes/123` → atualiza recurso  

### 2.4 Extensões WS-*

| Especificação | Função |
|---|---|
| **WS-Addressing** | Endpoint references; roteamento embutido no cabeçalho SOAP |
| **WS-ReliableMessaging** | Semânticas: *at-least-once*, *at-most-once*, *exactly-once*, *in-order* |
| **WS-Security** | Segurança de mensagem SOAP (assinatura + criptografia XML) |
| **WS-Coordination** | Coordenação de múltiplos serviços em transações distribuídas |

---

## 3. Implementação em Java: JAX-RPC

### 3.1 Proxy Estático (cliente)

```java
// Cliente JAX-RPC com proxy estático
// 1. Obtém o proxy do serviço
Stub proxy = (Stub)(new MyShapeListService_Impl().getShapeListPort());

// 2. Configura o endpoint
proxy._setProperty(
    javax.xml.rpc.Stub.ENDPOINT_ADDRESS_PROPERTY, 
    args[0]  // URL do serviço
);

// 3. Faz o cast para a interface de serviço
ShapeList aShapeList = (ShapeList) proxy;

// 4. Invoca o método (transparente — gera envelope SOAP internamente)
GraphicalObject g = aShapeList.getAllState(0);
System.out.println("type=" + g.type + " color=" + g.color);
```

### 3.2 Estratégias de Cliente JAX-RPC

| Estratégia | Quando usar |
|---|---|
| **Proxy estático** | Interface conhecida em tempo de compilação (caso comum) |
| **Proxy dinâmico** | Interface obtida via WSDL em runtime |
| **DII (Dynamic Invocation Interface)** | Construção dinâmica completa de chamadas |

### 3.3 Lado Servidor: Servlet Container

O serviço Web é implantado como um **servlet** em um container (Apache Tomcat, GlassFish):
- Container recebe a requisição HTTP POST com o envelope SOAP
- Deserializa XML → objetos Java
- Invoca o método do servlet
- Serializa a resposta Java → XML SOAP
- Retorna HTTP 200 com envelope de resposta

### 3.4 Comparação SOAP × CORBA (mesmo serviço ShapeList)

| Métrica | CORBA | SOAP |
|---|---|---|
| Tamanho da mensagem | 1× | **14× maior** |
| Tempo de RPC nulo | 1× | **882× mais lento** |
| Facilidade de uso na Internet | Difícil | Fácil |
| Firewall traversal | Problemático | Nativo (HTTP) |

**Conclusão:** SOAP perde em desempenho, mas ganha em interoperabilidade — trade-off justificado para escala Internet.

---

## 4. WSDL — Web Services Description Language

### 4.1 Estrutura Geral

WSDL tem duas partes: **abstrata** (reutilizável) e **concreta** (específica de binding):

```
PARTE ABSTRATA:
  types     → tipos de dados (XML Schema)
  message   → parâmetros de entrada e saída
  interface → operações (portType no WSDL 1.x)

PARTE CONCRETA:
  binding   → protocolo (SOAP/HTTP)
  service   → endereço (URL do endpoint)
```

### 4.2 Exemplo: Serviço ShapeList

**Parte abstrata — tipos e mensagens:**
```xml
<types>
  <schema xmlns="http://www.w3.org/2001/XMLSchema"
          targetNamespace="http://ShapeService.org/ws">
    <element name="GraphicalObject">
      <complexType>
        <sequence>
          <element name="type"     type="string"/>
          <element name="color"    type="string"/>
          <element name="isFilled" type="boolean"/>
        </sequence>
      </complexType>
    </element>
  </schema>
</types>

<!-- Mensagem de entrada para newShape -->
<message name="ShapeList_newShape">
  <part name="shape" element="tns:GraphicalObject"/>
</message>

<!-- Mensagem de saída (retorno: ID inteiro) -->
<message name="ShapeList_newShapeResponse">
  <part name="return" type="xsd:int"/>
</message>
```

**Interface abstrata:**
```xml
<interface name="ShapeList_PortType">
  <operation name="newShape" pattern="http://www.w3.org/...#in-out">
    <input  message="tns:ShapeList_newShape"/>
    <output message="tns:ShapeList_newShapeResponse"/>
  </operation>
  <operation name="allShapes" pattern="...">
    <output message="tns:ShapeList_allShapesResponse"/>
  </operation>
</interface>
```

**Parte concreta — binding e endpoint:**
```xml
<binding name="ShapeList_Binding" interface="tns:ShapeList_PortType"
         type="http://www.w3.org/2003/05/soap/bindings/HTTP/">
  <operation ref="tns:newShape">
    <input>
      <soap:body use="literal"/>
    </input>
  </operation>
</binding>

<service name="ShapeListService" interface="tns:ShapeList_PortType">
  <endpoint name="ShapeListPort"
            binding="tns:ShapeList_Binding"
            address="http://example.org/ShapeService"/>
</service>
```

### 4.3 Padrões de Troca de Mensagens (MEP)

| Padrão | Direção | Descrição |
|---|---|---|
| **In-Out** | → ← | Request-response (mais comum) |
| **In-Only** | → | Fire-and-forget (sem resposta) |
| **Robust In-Only** | → ← fault | Sem resposta, mas reporta falhas |
| **Out-In** | ← → | Servidor inicia (callback) |
| **Out-Only** | ← | Notificação unidirecional do servidor |
| **Robust Out-Only** | ← → fault | Notificação com reporte de falha |

---

## 5. UDDI — Universal Description, Discovery and Integration

### 5.1 Estruturas de Dados

```
businessEntity          ← informações da empresa
  └── businessService   ← serviços oferecidos
        └── bindingTemplate  ← endpoint técnico
              └── tModel     ← metadados técnicos (WSDL URL)
```

| Estrutura | Conteúdo |
|---|---|
| **businessEntity** | Nome da empresa, contato, classificação de negócio |
| **businessService** | Nome do serviço, descrição, categorias |
| **bindingTemplate** | URL de acesso, referência ao tModel |
| **tModel** | Ponteiro para WSDL; define fingerprint de interoperabilidade |

### 5.2 API UDDI

| Operação | Descrição |
|---|---|
| `get_businessDetail(key)` | Recupera empresa por chave |
| `get_serviceDetail(key)` | Recupera serviço por chave |
| `get_bindingDetail(key)` | Recupera binding por chave |
| `get_tModelDetail(key)` | Recupera tModel por chave |
| `find_business(criteria)` | Busca empresas por nome/categoria |
| `find_service(criteria)` | Busca serviços por nome/tipo |
| `find_tModel(criteria)` | Busca tModels (fingerprints de interface) |
| `save_xxx` / `delete_xxx` | Publicação e remoção de entradas |

### 5.3 Replicação do UDDI

O UDDI usa **timestamps vetoriais** para replicação:
- Todas as alterações em um servidor são propagadas para os demais
- Cada entrada carrega vetor de versão para detecção de conflitos e ordenação causal
- Garante consistência eventual entre os nós do registro global

---

## 6. Segurança em XML

### 6.1 Motivação: Segurança de Documento vs. Segurança de Canal

| Aspecto | TLS (segurança de canal) | XML Security (segurança de documento) |
|---|---|---|
| Escopo | Ponto a ponto (canal) | Partes do documento, persistente |
| Granularidade | Toda a mensagem | Elementos individuais do XML |
| Persistência | Só durante transmissão | Documento pode ser assinado/cifrado permanentemente |
| Intermediários | Não suporta assinaturas parciais | Diferentes partes assináveis por diferentes atores |

**Caso de uso típico:** Documento que circula por Alice → Bob → Carol, onde cada um valida/adiciona assinaturas em partes diferentes, sem violar as já existentes.

### 6.2 Algoritmos de Assinatura XML (Figura 9.16)

| Tipo | Algoritmo | Status |
|---|---|---|
| Resumo de mensagem | SHA-1 | **Exigido** |
| Codificação | Base64 | **Exigido** |
| Assinatura assimétrica | DSA com SHA-1 | **Exigido** |
| Assinatura assimétrica | RSA com SHA-1 | Recomendado |
| Assinatura simétrica (MAC) | HMAC-SHA-1 | **Exigido** |
| Canonização | XML Canônica | **Exigido** |

### 6.3 Algoritmos de Criptografia XML (Figura 9.17)

| Tipo | Algoritmo | Status |
|---|---|---|
| Cifra de bloco | TRIPLEDES, AES-128, AES-256 | **Exigido** |
| Cifra de bloco | AES-192 | Opcional |
| Codificação | Base64 | **Exigido** |
| Transporte de chave (assimétrica) | RSA-v1.5, RSA-OAEP | **Exigido** |
| Envoltório de chave simétrica | TRIPLEDES-KeyWrap, AES-128/256-KeyWrap | **Exigido** |
| Acordo de chave | Diffie-Hellman | Opcional |

### 6.4 Elementos XML Security

| Elemento | Função |
|---|---|
| `<Signature>` | Contém assinatura digital de partes do documento |
| `<SignedInfo>` | Referências para dados assinados + algoritmos usados |
| `<SignatureValue>` | Valor da assinatura calculado |
| `<KeyInfo>` | Informações opcionais para localizar a chave (certificado X.509, nome de chave, etc.) |
| `<EncryptedData>` | Engloba partes de dados cifrados |

### 6.5 XML Canônica

**Problema:** O mesmo documento XML pode ter representações diferentes (atributos em ordens distintas, codificações de caractere variadas) que são semanticamente equivalentes, mas bit-a-bit diferentes — o que invalidaria assinaturas digitais.

**Solução — XML Canônica:**
- Ordena atributos lexicograficamente
- Remove espaços de nomes supérfluos
- Padroniza quebras de linha
- Usa UTF-8 como codificação
- Adiciona atributos padrão

**Propriedade:** Quaisquer dois documentos XML equivalentes têm a mesma forma canônica.

**Contexto ancestral:** Ao canonizar um elemento, inclui-se o contexto dos ancestrais (espaços de nomes, atributos herdados). Isso impede que um elemento assinado seja movido para outro contexto sem invalidar a assinatura.

**Exclusive Canonical XML:** Variante que omite o contexto, permitindo elementos assinados em múltiplos contextos.

### 6.6 Serviço de Gerenciamento de Chaves XML (XKMS)

Fornece protocolos para **distribuir e registrar chaves públicas** para uso em assinaturas XML:
- Compatível com certificados X.509, SPKI e chaves PGP
- Exemplo: Alice quer cifrar e-mail para Bob → usa XKMS para obter chave pública de Bob
- Exemplo: Bob recebe documento assinado com certificado X.509 → pede ao XKMS para extrair a chave pública

---

## 7. Coordenação e Coreografia de Serviços Web

### 7.1 Motivação

A infraestrutura SOAP suporta apenas interações requisição-resposta simples. Aplicações reais exigem **sequências de operações com ordem específica** entre múltiplos serviços.

**Exemplo — Cenário do Agente de Viagens (Figura 9.18):**
1. Cliente solicita informações de voos, aluguel de carro e hotel
2. Agente reúne preços/disponibilidade → cliente escolhe ou refina
3. Cliente solicita reserva; agente verifica disponibilidade
4. Se todos disponíveis → confirma; caso contrário → oferece alternativas
5. Efetua depósito e fornece número de confirmação
6. Período de modificação/cancelamento até pagamento final

### 7.2 Transações vs. Atividades Longas

| Mecanismo | Adequado para |
|---|---|
| Transações atômicas + 2PC | Operações rápidas, recursos bloqueados brevemente |
| Protocolo relaxado (compensação) | Atividades longas (agente de viagens), onde 2PC seria impraticável |

No protocolo relaxado, cada participante altera o estado persistente quando conveniente; em caso de falha, **protocolo de compensação em nível de aplicação** desfaz as ações.

### 7.3 WS-Coordination

Modelo geral com funções de **coordenador** e **participante** capazes de atuar em protocolos específicos (ex.: transações distribuídas). Analogia com o modelo de transação distribuída do Capítulo 17.

### 7.4 Coreografia (WS-Choreography)

**Coreografia:** Descrição global de todos os caminhos válidos de interação entre um conjunto de serviços Web colaborando em uma tarefa.

**Usos da descrição de coreografia:**
- Gerar esboços de código para novos participantes
- Gerar testes automáticos
- Promover entendimento comum do protocolo
- Analisar possíveis situações de impasse (deadlock)

**Requisitos da linguagem de coreografia (W3C):**

| Requisito | Descrição |
|---|---|
| Composição hierárquica | Coreografias aninhadas e recursivas |
| Adição dinâmica | Novas instâncias de serviços existentes |
| Caminhos concorrentes/alternativos | Paralelismo e escolhas |
| Tempos limites variáveis | Ex.: diferentes prazos para manter reservas |
| Exceções | Mensagens fora de ordem, cancelamentos |
| Interações assíncronas | Callbacks |
| Passagem de referência | Ex.: operadora de aluguel consulta banco em nome do usuário |
| Limites de transação | Para permitir recuperação parcial |
| Documentação legível | Para seres humanos |

**Implementação:** WS-CDL (Web Services Choreography Definition Language) — linguagem declarativa XML baseada em WSDL, recomendação do W3C.

---

## 8. Aplicações de Serviços Web

### 8.1 Arquitetura Orientada a Serviços (SOA)

**SOA** é um conjunto de princípios de projeto onde sistemas distribuídos são construídos com **serviços pouco acoplados** que se descobrem dinamicamente e se coordenam via coreografia.

**Características:**
- Serviços com interfaces bem definidas e contratos claros
- Descoberta dinâmica (via UDDI ou outros registros)
- Interoperabilidade entre plataformas heterogêneas (CORBA org A ↔ .NET org B, ambas expondo serviços Web)
- **Integração B2B** (business-to-business): interoperabilidade entre diferentes empresas

**Mashup:** Novo serviço criado por desenvolvedor externo combinando dois ou mais serviços disponíveis.
- Exemplo: JBidwatcher — mashup Java que combina eBay API para gerenciar lances automaticamente
- Requisito: serviços com interfaces publicadas e comunidade de inovação aberta

### 8.2 Computação em Grade (Grid)

**Grade:** Middleware para **compartilhamento de recursos em larga escala** (arquivos, computadores, software, dados, sensores) entre grupos de usuários em organizações diferentes.

**Exemplo — World-Wide Telescope (Microsoft Research):**
- Unifica repositórios de astronomia do mundo (dados de terabytes/petabytes)
- Dados coletados por instrumentos em diferentes países e períodos
- Cada equipe gerencia seu repositório localmente
- Cientistas precisam cruzar dados de múltiplos instrumentos e épocas

**Requisitos típicos de aplicações de grade:**

| Requisito | Descrição |
|---|---|
| R1 | Acesso remoto a repositórios de arquivo distribuídos |
| R2 | Processamento local dos dados (onde são armazenados) — não transferir terabytes |
| R3 | Criação dinâmica de instâncias de serviço (como servents no modelo OO) |
| R4 | Metadados: características dos dados + características do serviço (custo, localização, carga) |
| R5 | Serviços de diretório baseados em metadados |
| R6 | Software para gerenciar consultas, transferências e reserva antecipada de recursos |

**Serviços Web satisfazem R1 e R2**; o restante fica a cargo do middleware de grade.

**OGSA — Open Grid Services Architecture:**
- Padrão para aplicações baseadas em grade
- Construído sobre serviços Web
- Implementado pelo **Toolkit Globus** (GT2 → GT3/OGSA 2002 → GT5 open source)
- Globus Alliance: evolução desde 1994/1997

**Outras aplicações de grade:**
- CERN/CMS: processamento de dados do acelerador de partículas
- Pesquisa farmacológica: simulação de moléculas para remédios
- Jogos online massivos: capacidade ociosa de clusters (www.butterfly.net)

### 8.3 Computação em Nuvem

**Definição:** Conjunto de serviços de aplicativo, armazenamento e computação baseados na Internet, suficientes para suportar a maioria das necessidades dos usuários — eliminando necessidade de software/armazenamento local.

**Grade vs. Nuvem:**

| Aspecto | Grade | Nuvem |
|---|---|---|
| Foco | Dados/computação científica intensiva | Serviços gerais para usuários finais |
| Modelo comercial | Colaborativo/acadêmico | Pago por uso |
| Origem histórica | Anterior (1994+) | Posterior; influenciada pela grade |

**Amazon Web Services (AWS):**

| Serviço | Descrição |
|---|---|
| **EC2** (Elastic Compute Cloud) | Máquinas virtuais sob demanda (instâncias), base Xen |
| **S3** (Simple Storage Service) | Armazenamento de dados não estruturados |
| **SimpleDB** | Armazenamento e consulta de dados estruturados |
| **SQS** (Simple Queue Service) | Filas de mensagens hospedadas |
| **Elastic MapReduce** | Computação distribuída MapReduce gerenciada |
| **FPS** (Flexible Payments Service) | Pagamentos eletrônicos |

**EC2 — detalhes:**
- Construído sobre o **hipervisor Xen** (Seção 7.7.2)
- Tipos de instância: padrão, alta memória, alta CPU, computação em grupo
- Suporta Windows Server, Linux, OpenSolaris
- **Endereço IP elástico:** associado à conta (não à instância), permite reatribuição automática em caso de falha sem intervenção do administrador
- Interface REST (80% das operações) + SOAP (20%)

---

## Mapa Conceitual

```
Serviços Web
├── Protocolo de comunicação
│   ├── SOAP
│   │   ├── Envelope (Header + Body + Fault)
│   │   ├── Transporte HTTP POST
│   │   └── Extensões: WS-Addressing, WS-ReliableMessaging
│   └── REST
│       └── URL + verbos HTTP (GET, PUT, DELETE, POST)
│
├── Descrição e Descoberta
│   ├── WSDL
│   │   ├── Parte Abstrata (types, message, interface)
│   │   └── Parte Concreta (binding, service/endpoint)
│   └── UDDI
│       ├── businessEntity → businessService → bindingTemplate → tModel
│       └── Replicação com timestamps vetoriais
│
├── Segurança
│   └── XML Security
│       ├── Assinaturas digitais (SHA-1, DSA, RSA, HMAC-SHA-1)
│       ├── Criptografia (AES, TRIPLEDES, RSA, DH)
│       ├── XML Canônica (forma canônica = forma única)
│       └── XKMS (gerenciamento de chaves)
│
├── Coordenação
│   ├── WS-Coordination (coordenador + participantes)
│   └── Coreografia (WS-CDL)
│       └── Descrição global de interações entre serviços
│
└── Aplicações
    ├── SOA (baixo acoplamento, B2B, mashup)
    ├── Grid (OGSA, Globus, World-Wide Telescope)
    └── Cloud (AWS: EC2/S3/SQS/MapReduce, REST, Xen)
```

---

## Relevância para Sistemas de Informação

| Contexto SI | Conceito do Capítulo | Aplicação Prática |
|---|---|---|
| Integração de sistemas corporativos | SOA + Serviços Web | ERP, CRM, SCM interoperando via SOAP/REST |
| APIs de e-commerce | REST + SOAP | Pagamentos, estoque, pedidos expostos como serviços |
| Segurança de transações | XML Security + WS-Security | NFe brasileira usa XML Security para assinaturas digitais |
| Infraestrutura de TI | Computação em nuvem (AWS EC2) | Redução de CAPEX, elasticidade automática |
| Big Data / Pesquisa | Computação em grade (Grid) | CERN, bioinformática, meteorologia |
| Microserviços | SOA evoluída | Netflix, Uber, Amazon — arquiteturas baseadas em serviços |
| Mashups e inovação | Composição de serviços | Integração de APIs públicas (Google Maps + imóveis, etc.) |
| Nota Fiscal Eletrônica (NF-e) | XML Security + SOAP | Padrão nacional brasileiro usa SOAP + assinatura XML |

---

## Erros Conceituais Comuns

1. **"SOAP e REST são a mesma coisa"**
   - Errado: REST é um estilo arquitetural baseado em recursos/URL/verbos HTTP; SOAP é um protocolo de mensagem XML sobre HTTP POST.

2. **"WSDL define apenas a interface"**
   - Incompleto: WSDL tem parte abstrata (interface) e parte concreta (binding de protocolo + endereço real do serviço).

3. **"UDDI é apenas um registro de nomes"**
   - Incompleto: é também um serviço de **diretório** (busca por critérios) e de **descoberta** (localiza serviços compatíveis com uma interface, via tModel).

4. **"XML Security substitui TLS"**
   - Errado: são complementares. TLS protege o canal de transmissão; XML Security protege o documento persistentemente, permitindo assinaturas parciais por múltiplos atores.

5. **"Grid e Cloud são a mesma coisa"**
   - Errado: Grid foca em computação científica intensiva e compartilhamento colaborativo; Cloud é mais geral, com modelo comercial pago por uso e serviços para usuários finais.

6. **"Serviços Web suportam referências a objetos remotos"**
   - Errado: serviços Web explicitamente **não** suportam instanciação remota, servents nem retorno de referências remotas — é uma das diferenças em relação ao modelo de objetos distribuídos.

7. **"WS-Choreography e WS-Coordination são a mesma especificação"**
   - Errado: WS-Coordination define a infraestrutura de coordenador/participante; WS-Choreography (WS-CDL) define a **linguagem declarativa** para descrever o fluxo de interações observáveis.

---

## Questões de Revisão

1. Explique por que os serviços Web foram criados quando já existia o middleware de objetos distribuídos (CORBA, Java RMI). Quais problemas eles resolvem que o middleware convencional não resolvia?

2. Descreva a estrutura de um envelope SOAP para uma chamada ao método `newShape(GraphicalObject g)` do serviço ShapeList. Inclua o elemento Fault para o caso em que a lista está cheia.

3. Compare REST e SOAP em termos de: (a) modelo de interação, (b) overhead de comunicação, (c) facilidade de uso com firewalls. Por que a Amazon adotou REST para 80% de suas operações?

4. Explique a diferença entre a parte abstrata e a parte concreta de uma descrição WSDL. Por que essa separação é vantajosa?

5. Um cliente precisa descobrir todos os serviços de reserva de voo disponíveis em um registro UDDI. Descreva quais operações ele usaria e como tModel ajuda a garantir compatibilidade de interface.

6. Por que a XML Canônica é necessária para assinaturas digitais XML? O que aconteceria sem ela ao mover um elemento assinado para um contexto diferente?

7. Descreva o cenário do agente de viagens (Figura 9.18) e explique por que um protocolo de commit em duas fases seria inadequado para coordenar suas ações. Qual alternativa o capítulo sugere?

8. Explique o conceito de **mashup** no contexto de SOA. Quais pré-requisitos devem ser satisfeitos para que a cultura de mashup floresça?

9. Quais são os seis requisitos (R1–R6) de uma aplicação de grade típica? Quais deles os serviços Web satisfazem diretamente e quais exigem middleware adicional?

10. O EC2 da Amazon usa Xen como hipervisor. Explique como o conceito de **endereço IP elástico** do EC2 contribui para a disponibilidade do serviço em caso de falha de uma instância virtual.

---

## Referência

> COULOURIS, G. et al. **Sistemas Distribuídos: Conceitos e Projeto**. 5ª ed. Porto Alegre: Bookman, 2013. Capítulo 9, pp. 381–422.
