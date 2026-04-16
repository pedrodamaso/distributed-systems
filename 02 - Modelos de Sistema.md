# Sistemas Distribuídos — Capítulo 2: Modelos de Sistema
**Livro:** Coulouris et al. — *Sistemas Distribuídos: Conceitos e Projeto*
**Disciplina:** Sistemas Distribuídos | Graduação em Sistemas de Informação

---

## Objetivo de Aprendizagem

Ao final do estudo deste capítulo, o aluno deve ser capaz de:

- Distinguir os três tipos de modelos usados para descrever sistemas distribuídos
- Identificar as gerações históricas dos sistemas distribuídos e suas características
- Descrever as arquiteturas cliente-servidor e peer-to-peer, comparando suas vantagens e limitações
- Explicar os padrões arquitetônicos mais comuns: camadas lógicas, camadas físicas, proxy, broker
- Compreender o modelo de interação e as implicações de sistemas síncronos e assíncronos
- Classificar e analisar os tipos de falhas em processos e canais de comunicação
- Identificar as ameaças ao modelo de segurança e as técnicas para mitigá-las

---

## Pré-requisitos

- Capítulo 1: definição de sistema distribuído, desafios (heterogeneidade, segurança, escalabilidade, falhas)
- Noções de redes de computadores (protocolos, mensagens, latência)
- Conceito de processo e thread em sistemas operacionais

---

## Visão Geral: Os Três Tipos de Modelos

O Capítulo 2 apresenta uma **estrutura conceitual de três camadas** para raciocinar sobre sistemas distribuídos:

```
┌────────────────────────────────────────────────────┐
│  MODELOS FÍSICOS                                   │
│  "Como o hardware evoluiu?"                        │
│  → Gerações dos sistemas distribuídos              │
├────────────────────────────────────────────────────┤
│  MODELOS DE ARQUITETURA                            │
│  "Como os componentes se organizam e interagem?"   │
│  → Cliente-servidor, P2P, camadas, padrões         │
├────────────────────────────────────────────────────┤
│  MODELOS FUNDAMENTAIS                              │
│  "Quais propriedades formais o sistema possui?"    │
│  → Interação, falhas, segurança                    │
└────────────────────────────────────────────────────┘
```

Esses modelos são complementares. O modelo físico descreve o substrato; o modelo arquitetural descreve a organização lógica; os modelos fundamentais permitem raciocinar formalmente sobre o comportamento do sistema.

---

## 1. Modelos Físicos — As Gerações dos Sistemas Distribuídos

Modelos físicos caracterizam o hardware subjacente e como ele evoluiu ao longo do tempo.

### Três Gerações

| Geração | Período | Características Principais |
|---|---|---|
| **Primeira** | 1970–1985 | 10 a 100 nós em LAN, serviços básicos (e-mail, transferência de arquivos), ambiente homogêneo, escala pequena |
| **Segunda** | 1985–2000 | Escala Internet (milhões de nós), ambiente heterogêneo, surgimento da Web, computação cliente-servidor em grande escala |
| **Terceira** | 2000–atual | Computação móvel e ubíqua, dispositivos embarcados, computação em nuvem, sistemas altamente dinâmicos e pervasivos |

**Por que isso importa?** Os desafios de cada geração moldaram as soluções arquitetônicas e os protocolos estudados no restante do livro. Soluções projetadas para 100 nós homogêneos falham em bilhões de nós heterogêneos.

---

## 2. Modelos de Arquitetura

Modelos de arquitetura descrevem **como os componentes de software interagem** para formar o sistema. São compostos por:

- **Entidades comunicantes:** processos, objetos, componentes, serviços Web
- **Paradigmas de comunicação:** como as entidades trocam informações
- **Papéis e responsabilidades:** quem faz o quê (cliente/servidor, par/par)
- **Posicionamento:** como os componentes são distribuídos fisicamente
- **Padrões arquitetônicos:** estruturas recorrentes que resolvem problemas comuns

---

### 2.1 Paradigmas de Comunicação

| Paradigma | Descrição | Exemplos |
|---|---|---|
| **Chamada de procedimento remoto (RPC)** | Invoca função em processo remoto como se fosse local | Java RMI, gRPC |
| **Invocação de método remoto (RMI)** | Invoca método em objeto remoto; suporta herança e polimorfismo | Java RMI, CORBA |
| **Comunicação indireta** | Produtor e consumidor desacoplados no tempo e no espaço | Filas de mensagens, pub-sub, memória compartilhada distribuída |

---

### 2.2 Arquitetura Cliente-Servidor

O modelo mais simples e direto de compartilhamento de recursos em sistemas distribuídos.

```
[Cliente] ──── requisição ────► [Servidor]
[Cliente] ◄─── resposta   ──── [Servidor]
```

**Limitação fundamental:** a centralização do serviço em um único computador limita a escalabilidade. Soluções parciais incluem múltiplos servidores, cache e clusters — mas nenhuma resolve o problema de fundo: distribuir a carga entre um número muito grande de nós.

---

### 2.3 Arquitetura Peer-to-Peer (P2P)

No modelo P2P, todos os processos desempenham papéis equivalentes (**peers**), executando o mesmo programa e oferecendo as mesmas interfaces uns para os outros.

**Motivação:** explorar os recursos de hardware e de rede dos próprios usuários do serviço, de modo que a capacidade disponível **cresce com o número de usuários** — exatamente o oposto do gargalo do modelo cliente-servidor.

**Características:**
- Grande número de objetos distribuídos entre os peers
- Cada peer armazena apenas uma fração do banco de dados total
- Replicação entre peers garante disponibilidade mesmo quando nós saem da rede
- Carga de armazenamento, processamento e comunicação é dividida por todos

**Exemplos históricos e atuais:**

| Sistema | Tipo | Observação |
|---|---|---|
| Napster | Compartilhamento de músicas | Arquitetura híbrida: índice centralizado, transferências P2P |
| BitTorrent | Compartilhamento de arquivos | Totalmente descentralizado para transferências |
| EVE Online | MMOG | Usa cluster centralizado; outros MMOGs usam P2P distribuído |

**Complexidade:** mais difícil que cliente-servidor. A necessidade de localizar objetos, manter réplicas atualizadas e coordenar entre centenas de milhares de nós exige algoritmos sofisticados (ex: tabelas de hash distribuídas — DHT, discutidas no Cap. 10).

---

### 2.4 Posicionamento de Serviços e Estratégias Complementares

O **posicionamento** define onde cada serviço ou objeto é executado na infraestrutura física. É uma decisão de projeto crítica que afeta desempenho, confiabilidade e segurança.

#### 2.4.1 Mapeamento em Múltiplos Servidores

Um serviço pode ser implementado por vários processos servidores que cooperam. Duas estratégias:

| Estratégia | Descrição | Exemplo |
|---|---|---|
| **Particionamento** | Dados divididos entre servidores diferentes | Cada servidor Web gerencia seu próprio conjunto de recursos |
| **Replicação** | Cópias dos mesmos dados em vários servidores | NIS (Network Information Service): arquivo de senhas replicado em toda a rede local |

**Clusters** são arquiteturas fortemente acopladas com centenas ou milhares de nós, usados para alta disponibilidade e balanceamento de carga.

#### 2.4.2 Cache

> **Cache** é um armazenamento local de objetos recentemente usados, colocado mais próximo do cliente do que a origem real dos dados.

**Funcionamento:**
1. Requisição chega → verifica se há cópia válida na cache
2. Se sim (cache hit): entrega local sem acessar o servidor
3. Se não (cache miss): acessa o servidor original e armazena localmente

**Tipos:**
- **Cache local no cliente:** o navegador mantém páginas visitadas no disco local
- **Servidor proxy:** cache compartilhada para múltiplos clientes de uma organização

```
[Cliente A] ──►┐
[Cliente B] ──►├──► [Proxy/Cache] ──► [Servidor Web remoto]
[Cliente C] ──►┘
```

**Benefícios:** reduz tráfego de rede, diminui carga no servidor original, melhora tempo de resposta.

#### 2.4.3 Código Móvel

Código que pode ser **transferido de um computador para outro e executado no destino**, reduzindo a latência de interação (o código roda localmente, sem depender da rede para cada operação).

**Exemplos:**
- **Applets Java:** baixados do servidor Web e executados no navegador
- **JavaScript:** baixado com a página HTML, executa no navegador
- **Modelo push:** o servidor envia código que fica "ouvindo" atualizações (ex: cotações de ações em tempo real)

**Risco:** código móvel é uma ameaça em potencial à segurança. Navegadores restringem o acesso de applets a recursos locais por meio de "sandbox".

#### 2.4.4 Agentes Móveis

> **Agente móvel** é um programa em execução (código + dados) que se desloca de computador em computador em uma rede, realizando tarefas em nome de um usuário e retornando com os resultados.

**Vantagem sobre requisições remotas:** substitui múltiplas chamadas remotas por operações locais em cada site visitado, reduzindo tráfego de rede.

**Usos potenciais:** comparação de preços em múltiplos fornecedores, instalação de software, coleta de informações distribuídas.

**Limitações práticas:** riscos de segurança (o agente pode ter acesso indevido aos recursos do host visitado) e dificuldade de completar tarefas quando o acesso é negado. Na prática, Web crawlers com requisições remotas têm se mostrado mais robustos.

---

### 2.5 Padrões Arquitetônicos

Padrões são **estruturas recorrentes** que provaram funcionar bem em determinadas circunstâncias. São blocos de construção, não soluções completas.

#### 2.5.1 Camadas Lógicas (Layers)

Organização **vertical** do sistema em camadas de abstração, onde cada camada usa apenas os serviços da camada imediatamente abaixo.

```
┌─────────────────────────────┐
│   Aplicativos e Serviços    │
├─────────────────────────────┤
│        Middleware           │  ← abstrai heterogeneidade
├─────────────────────────────┤
│      Sistema Operacional    │
├─────────────────────────────┤
│  Plataforma (HW + SO base)  │  ← Intel x86/Linux, ARM/Android...
└─────────────────────────────┘
```

**Plataforma:** camadas de HW e SW de nível mais baixo; fornece API para comunicação e coordenação.

**Middleware:** camada extra que mascara a heterogeneidade e eleva o nível das atividades de comunicação. Oferece abstrações como:
- Invocação de método remoto
- Comunicação em grupo
- Notificação de eventos
- Particionamento e replicação de objetos compartilhados
- Transmissão multimídia em tempo real

#### 2.5.2 Camadas Físicas (Tiers)

Organização **horizontal** que mapeia a funcionalidade da aplicação em servidores físicos distintos. Três dimensões funcionais:

| Camada | Responsabilidade |
|---|---|
| **Apresentação** | Interação com o usuário, renderização da interface |
| **Lógica de aplicação** | Regras de negócio, processamento |
| **Dados** | Armazenamento persistente (banco de dados) |

**Arquitetura de duas camadas físicas (2-tier):**
- Lógica dividida entre cliente e servidor
- Menor latência (uma troca de mensagens por operação)
- Desvantagem: lógica de aplicação fragmentada entre dois processos

**Arquitetura de três camadas físicas (3-tier):**
```
[Cliente/Apresentação] ──► [Servidor de Aplicação] ──► [Banco de Dados]
    Camada 1                    Camada 2                  Camada 3
```
- Cada camada tem função bem definida
- Lógica de aplicação em um único lugar → maior manutenibilidade
- Facilita cliente "magro" (thin client) na camada 1
- Mais tráfego de rede e maior complexidade de gerenciamento
- **Wikipedia** adota arquitetura de múltiplas camadas para lidar com até 60.000 pedidos de página/segundo

#### 2.5.3 AJAX (Asynchronous JavaScript and XML)

O modelo padrão de interação Web (requisição HTTP → recebe página inteira → renderiza) tem três limitações sérias:

1. O usuário não pode interagir com a página enquanto aguarda a resposta do servidor
2. Atualizar uma pequena parte da página exige baixar e renderizar a página inteira
3. O conteúdo exibido não pode ser atualizado em resposta a mudanças no servidor

**AJAX resolve esses problemas** permitindo que código JavaScript no navegador faça requisições HTTP ao servidor de forma **assíncrona** e atualize apenas a parte da página relevante com os dados recebidos:

```javascript
new Ajax.Request('scores.php?game=Arsenal:Liverpool',
    {onSuccess: updateScore});

function updateScore(request) {
    // analisa o resultado e atualiza apenas a célula do placar
}
```

**Mecanismo:** objeto `XmlHttpRequest` envia requisição HTTP sem bloquear a interface. O navegador continua respondendo ao usuário; quando a resposta chega, a função de callback atualiza seletivamente a página.

**Uso em 3 camadas:** o componente JavaScript (camada 1) chama o servidor de aplicação (camada 2), que faz uma consulta SQL síncrona ao banco de dados (camada 3).

**Exemplo canônico:** Google Maps — ao arrastar o mapa, as tiles vizinhas são carregadas em segundo plano via AJAX sem recarregar a página.

#### 2.5.4 Clientes "Magros" (Thin Clients) e VNC

> **Cliente magro (thin client)** é uma camada de software que apresenta uma interface gráfica local ao usuário enquanto executa aplicativos em um servidor remoto.

**Motivação:** transferir a complexidade computacional do equipamento do usuário para serviços de rede/nuvem, permitindo que dispositivos simples (smartphones, terminais baratos) acessem sofisticados serviços.

**Desvantagem:** para atividades gráficas intensas (CAD, processamento de imagens), os atrasos de rede tornam a experiência inaceitável.

**VNC (Virtual Network Computing):**
- Opera sobre framebuffers: apenas pixels são transmitidos entre cliente e servidor
- Operação primitiva: "coloque este retângulo de pixels neste local da tela"
- Funciona com qualquer SO ou aplicativo
- Permite acesso remoto completo à interface gráfica de qualquer lugar

---

#### 2.5.5 Outros Padrões Recorrentes

| Padrão | Descrição | Uso em SD |
|---|---|---|
| **Proxy** | Objeto local que representa um objeto remoto com a mesma interface | Suporta transparência de localização em RPC e RMI; o programador faz chamadas locais sem saber que são remotas |
| **Broker** | Intermediário que combina solicitantes e provedores de serviço | RMI Registry, CORBA Naming Service, descoberta de serviços |
| **Reflexão** | Mecanismo para introspecção (descobrir propriedades do sistema) e intercessão (modificar comportamento dinamicamente) | Middleware refletivo configurável; RMI usa introspecção Java para despacho genérico |

---

## 3. Modelos Fundamentais

Modelos fundamentais descrevem **propriedades formais** comuns a todos os sistemas distribuídos, independentemente da arquitetura. Existem três:

---

### 3.1 Modelo de Interação

O modelo de interação trata das **restrições que a comunicação impõe ao comportamento** de sistemas distribuídos. Duas dimensões centrais:

#### 3.1.1 Desempenho da Comunicação

| Conceito | Definição | Impacto |
|---|---|---|
| **Latência** | Tempo entre o início do envio de uma mensagem e o início do recebimento | Afeta tempo de resposta em operações síncronas |
| **Largura de banda** | Volume de informação que pode ser transmitido por unidade de tempo | Limita throughput em transferências grandes |
| **Jitter** | Variação no tempo de entrega de mensagens sucessivas | Crítico para mídia contínua (áudio/vídeo): causa distorções se muito alto |

#### 3.1.2 O Problema do Tempo Global

**Não existe relógio global confiável em sistemas distribuídos.** Embora todos os computadores tenham relógios locais, eles derivam (drift) em velocidades ligeiramente diferentes, tornando impossível uma sincronização perfeita apenas por troca de mensagens.

Consequência: **não é possível determinar a ordem exata de eventos em computadores diferentes** com base apenas nos relógios locais.

#### 3.1.3 Sistemas Síncronos vs. Assíncronos

| Aspecto | Sistema Síncrono | Sistema Assíncrono |
|---|---|---|
| **Tempo de execução de cada passo** | Existe um limite mínimo e máximo conhecido | Sem limite |
| **Atraso na entrega de mensagens** | Existe um limite máximo conhecido | Sem limite |
| **Deriva do relógio** | Existe um limite máximo conhecido | Sem limite |
| **Facilidade de raciocínio** | Mais fácil (limites conhecidos) | Mais difícil |
| **Realismo** | Não é garantido na Internet real | Melhor modelo para Internet |

> **Sistema síncrono** é mais fácil de projetar porque as suposições sobre limites de tempo permitem detectar falhas via timeout. Porém, a **Internet real é assíncrona** — não há garantia de latência máxima. A maioria das soluções práticas assume assincronicidade e lida com as consequências.

**Implicação prática:** algoritmos projetados para sistemas síncronos podem falhar em sistemas assíncronos. Por exemplo, um timeout que assume entrega em no máximo 1 segundo pode gerar falsos positivos quando a rede está congestionada.

---

### 3.2 Modelo de Falhas

O modelo de falhas define e **classifica os tipos de falhas** que podem ocorrer em sistemas distribuídos, permitindo projetar sistemas que tratam cada tipo apropriadamente.

#### 3.2.1 Falhas de Processo

| Tipo | Descrição | Detectabilidade |
|---|---|---|
| **Falha por omissão (fail-stop)** | O processo para de executar e outros processos detectam isso | Detectável |
| **Falha por colapso (crash)** | O processo para de executar, mas outros processos podem não detectar | Pode ser indetectável |
| **Falha arbitrária (Bizantina)** | O processo continua executando, mas produz resultados incorretos ou age maliciosamente | Muito difícil de detectar |

#### 3.2.2 Falhas de Comunicação

| Tipo | Descrição |
|---|---|
| **Omissão no envio** | Processo falha em colocar a mensagem no buffer de envio da rede |
| **Omissão no canal** | Mensagem enviada não chega ao buffer de recepção (pacote perdido em trânsito) |
| **Omissão na recepção** | Mensagem chega ao buffer mas o processo não a lê |
| **Falha arbitrária de canal** | Mensagens corrompidas, duplicadas, entregues fora de ordem, ou mensagens fantasmas geradas |

#### 3.2.3 Falhas Bizantinas

> **Falha Bizantina (Arbitrary Failure)** é a pior classe de falha: um componente pode exibir qualquer comportamento, incluindo enviar mensagens contraditórias para diferentes partes do sistema, simular funcionamento correto ou agir de forma deliberadamente maliciosa.

**Por que é o pior caso?** Um componente com falha por colapso simplesmente para; é fácil detectar. Um componente Bizantino pode enviar dados incorretos que parecem corretos para uns e incorretos para outros, tornando o consenso extremamente difícil.

**Exemplo:** em um sistema de votação distribuído, um processo Bizantino pode votar "sim" para alguns nós e "não" para outros, impedindo que o sistema chegue a um acordo consistente.

#### 3.2.4 Detecção de Falhas

Como detectar que um processo remoto falhou?

- **Timeout:** aguarda um tempo máximo pela resposta; se não houver resposta, suspeita de falha
- **Problema:** em um sistema assíncrono, ausência de resposta pode significar:
  - O processo falhou (crash)
  - A mensagem está atrasada na rede
  - A resposta está atrasada

Portanto, em sistemas assíncronos, **não é possível distinguir com certeza entre falha e atraso**. Detectores de falha apenas produzem **suspeitas**, não certezas.

---

### 3.3 Modelo de Segurança

O modelo de segurança identifica **ameaças** ao sistema e as técnicas para mitigá-las, estabelecendo as bases para o projeto de sistemas seguros.

#### 3.3.1 Ameaças a Processos

Um adversário pode:
- Enviar mensagens para qualquer processo se passando por outro (spoofing)
- Tentar acessar recursos que não lhe são autorizados
- Capturar e reutilizar mensagens legítimas (replay attack)

#### 3.3.2 Ameaças aos Canais de Comunicação

Um adversário com acesso ao canal de rede pode:

| Ameaça | Descrição |
|---|---|
| **Interceptação (eavesdropping)** | Copiar mensagens sem o conhecimento das partes |
| **Adulteração (tampering)** | Alterar o conteúdo de mensagens em trânsito |
| **Injeção** | Inserir mensagens falsas no canal |
| **Repetição (replay)** | Reenviar mensagens anteriormente capturadas |

#### 3.3.3 Canais Seguros e Criptografia

A solução para as ameaças acima é o uso de **criptografia** para estabelecer **canais seguros**:

> **Canal seguro** é um canal de comunicação que oferece autenticação (garante a identidade das partes) e confidencialidade (garante que apenas as partes autorizadas leem o conteúdo).

**Duas técnicas principais:**

| Técnica | Descrição | Uso |
|---|---|---|
| **Criptografia simétrica** | A mesma chave cifra e decifra (ex: AES) | Rápida; usada após estabelecer a chave segura |
| **Criptografia de chave pública (assimétrica)** | Par de chaves: pública (cifra) e privada (decifra) — ex: RSA | Autentica identidade e estabelece chave de sessão |

**Fluxo típico:**
1. Troca de chaves usando criptografia assimétrica (ex: protocolo Diffie-Hellman)
2. Autenticação mútua das partes
3. Comunicação cifrada com chave simétrica de sessão

---

## 4. Síntese — Mapa Conceitual do Capítulo

```
MODELOS DE SISTEMA
│
├── FÍSICO: Gerações
│   ├── 1ª: LANs homogêneas, pequena escala
│   ├── 2ª: Internet, escala global, Web
│   └── 3ª: Nuvem, mobile, ubíqua
│
├── ARQUITETURAL: Como os componentes se organizam
│   ├── Entidades: processos, objetos, serviços
│   ├── Paradigmas: RPC, RMI, comunicação indireta
│   ├── Papéis: Cliente-servidor | Peer-to-peer
│   ├── Posicionamento:
│   │   ├── Múltiplos servidores (partição/replicação)
│   │   ├── Cache (local/proxy)
│   │   ├── Código móvel (applets, JavaScript)
│   │   └── Agentes móveis
│   └── Padrões:
│       ├── Camadas lógicas (plataforma → middleware → app)
│       ├── Camadas físicas (1-tier, 2-tier, 3-tier, n-tier)
│       ├── AJAX (atualização assíncrona de páginas Web)
│       ├── Thin client / VNC
│       ├── Proxy (transparência de localização)
│       ├── Broker (descoberta de serviço)
│       └── Reflexão (introspecção e intercessão)
│
└── FUNDAMENTAL: Propriedades formais
    ├── Interação:
    │   ├── Desempenho: latência, largura de banda, jitter
    │   ├── Problema do tempo global: sem relógio compartilhado
    │   └── Síncrono vs. Assíncrono
    ├── Falhas:
    │   ├── Processo: omissão, colapso, Bizantina
    │   ├── Canal: omissão, arbitrária
    │   └── Detecção: timeouts → suspeitas (não certezas)
    └── Segurança:
        ├── Ameaças: spoofing, interceptação, adulteração, replay
        └── Canais seguros: criptografia simétrica + assimétrica
```

---

## 5. Relação com Sistemas de Informação

| Conceito do Capítulo | Aplicação Prática em SI |
|---|---|
| Arquitetura 3-tier | Todo sistema web corporativo (front-end, back-end, banco de dados) |
| Cache / Proxy | CDNs em e-commerce, cache de sessão em sistemas ERP |
| AJAX | Dashboards analíticos, sistemas ERP com atualização em tempo real |
| Peer-to-peer | Sistemas de compartilhamento de documentos corporativos, blockchain |
| Modelo de falhas | Projeto de sistemas de missão crítica: bancos, hospitais, e-governo |
| Canais seguros (TLS/HTTPS) | Toda transação financeira online; proteção de dados de clientes |
| Thin client / VNC | Ambientes corporativos com acesso remoto a sistemas legados |
| Broker | Service discovery em microsserviços (ex: Kubernetes, Consul) |

---

## 6. Erros Comuns dos Alunos

| Equívoco | Correção |
|---|---|
| Confundir camadas lógicas (layers) com camadas físicas (tiers) | Layers = organização de abstração vertical (plataforma/middleware/app); Tiers = distribuição física de componentes em servidores diferentes |
| Achar que P2P elimina todos os problemas de escalabilidade | P2P melhora escalabilidade, mas introduz complexidade de coordenação, descoberta de recursos e tolerância a falhas muito maior |
| Supor que sistema síncrono é sempre melhor | Sistemas síncronos são mais fáceis de projetar, mas a Internet real é assíncrona; soluções baseadas em suposições síncronas podem falhar |
| Confundir falha por colapso com falha Bizantina | Colapso: processo para e fica silencioso; Bizantina: processo continua ativo mas se comporta de forma incorreta ou maliciosa |
| Achar que timeout detecta falha com certeza | Em sistemas assíncronos, timeout apenas gera suspeita — não é possível distinguir falha de atraso com certeza |
| Confundir proxy (padrão arquitetural) com servidor proxy (cache) | Proxy arquitetural = objeto local que representa objeto remoto; servidor proxy = intermediário de cache para requisições Web |

---

## 7. Questões para Revisão e Discussão

1. Quais são os três tipos de modelos apresentados no capítulo? Por que cada um é necessário? O que cada um responde que os outros não respondem?

2. Compare as arquiteturas cliente-servidor e peer-to-peer em termos de: escalabilidade, complexidade de implementação e tolerância a falhas. Em que cenários cada uma é mais adequada?

3. Explique a diferença entre particionamento e replicação como estratégias de múltiplos servidores. Dê um exemplo de cada estratégia aplicada a um sistema de informação real.

4. Por que um sistema síncrono é mais fácil de raciocinar do que um assíncrono? Quais riscos surgem ao usar suposições síncronas em um ambiente que é na prática assíncrono?

5. Classifique os seguintes cenários quanto ao tipo de falha: (a) servidor de banco de dados para de responder sem aviso; (b) roteador descarta aleatoriamente 10% dos pacotes; (c) processo envia respostas corretas para alguns clientes e incorretas para outros.

6. Por que falhas Bizantinas são consideradas o pior caso? Qual a relevância desse tipo de falha para sistemas financeiros ou de controle?

7. Qual a diferença entre um canal seguro e um canal cifrado? O que a autenticação acrescenta à confidencialidade?

8. Descreva como a arquitetura de três camadas físicas (3-tier) de um sistema de e-commerce mapeia as camadas de apresentação, lógica de negócio e dados. Quais componentes residem em cada camada?

---

## Referência

COULOURIS, G. et al. **Sistemas Distribuídos: Conceitos e Projeto**. 5. ed. Porto Alegre: Bookman, 2013. Capítulo 2, p. 37–76.