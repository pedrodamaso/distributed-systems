# Sistemas Distribuídos — Capítulo 1: Caracterização de Sistemas Distribuídos
**Livro:** Coulouris et al. — *Sistemas Distribuídos: Conceitos e Projeto*
**Disciplina:** Sistemas Distribuídos | Graduação em Sistemas de Informação

---

## Objetivo de Aprendizagem

Ao final do estudo deste capítulo, o aluno deve ser capaz de:

- Definir sistema distribuído e identificar suas características fundamentais
- Reconhecer exemplos reais de sistemas distribuídos e sua relevância atual
- Compreender as principais tendências que impulsionam a evolução dos sistemas distribuídos
- Explicar o conceito de compartilhamento de recursos e o modelo cliente-servidor
- Identificar e descrever os oito grandes desafios do projeto de sistemas distribuídos
- Relacionar os conceitos teóricos com a arquitetura da World Wide Web

---

## Pré-requisitos

- Conceitos básicos de redes de computadores (IP, TCP/IP, protocolos)
- Noções de sistemas operacionais (processos, threads, comunicação entre processos)
- Familiaridade com arquitetura cliente-servidor

---

## 1. Definição e Características Fundamentais

> **Sistema Distribuído** é aquele no qual os componentes de hardware ou software, localizados em computadores interligados em rede, comunicam-se e coordenam suas ações apenas enviando mensagens entre si.
> — Coulouris et al.

Dessa definição decorrem **três consequências essenciais**:

| Característica | Descrição |
|---|---|
| **Concorrência** | Múltiplos programas executam simultaneamente e podem compartilhar recursos. A capacidade do sistema cresce com a adição de mais recursos na rede. |
| **Inexistência de relógio global** | Não existe uma noção única e precisa de tempo compartilhada entre todos os nós. A coordenação depende exclusivamente da troca de mensagens, o que impõe limites à sincronização. |
| **Falhas independentes** | Cada componente pode falhar isoladamente, sem que os demais saibam imediatamente. A falha de rede pode isolar nós que continuam funcionando normalmente. |

**Por que isso importa?** Cada uma dessas três características exige soluções específicas de projeto. Ignorar qualquer uma delas resulta em sistemas frágeis, inconsistentes ou incorretos.

---

## 2. Exemplos Representativos de Sistemas Distribuídos

### 2.1 Mecanismos de Busca na Web (ex: Google)

A infraestrutura do Google é um dos maiores sistemas distribuídos da história da computação. Seus elementos principais:

- Milhares de computadores em data centers distribuídos pelo mundo
- **Sistema de arquivos distribuído** otimizado para leitura em alta velocidade de arquivos muito grandes
- **Sistema de armazenamento distribuído estruturado** para acesso rápido a grandes volumes de dados
- **Serviço de bloqueio distribuído** para garantir coordenação e consistência
- **Modelo de programação distribuída** (ex: MapReduce) para processamento paralelo massivo

> **Relevância para SI:** Empresas de todos os portes constroem infraestruturas similares (em menor escala) para analytics, e-commerce e buscas internas.

### 2.2 Jogos Online Massivos (MMOGs)

MMOGs como *EVE Online* e *EverQuest* exigem que dezenas de milhares de usuários simultâneos compartilhem um mundo virtual persistente com tempos de resposta muito baixos.

Três abordagens arquiteturais foram desenvolvidas:

| Arquitetura | Descrição | Exemplo |
|---|---|---|
| **Cliente-servidor centralizado** | Estado único do mundo mantido em cluster de servidores | EVE Online |
| **Servidores múltiplos particionados** | Universo dividido entre vários servidores geograficamente distribuídos | EverQuest |
| **Peer-to-peer descentralizado** | Cada participante contribui com recursos para hospedar o jogo | Pesquisa acadêmica |

### 2.3 Sistemas de Negócios Financeiros

Sistemas financeiros são pioneiros no uso de sistemas distribuídos. Características marcantes:

- Processamento de múltiplos **fluxos de eventos** em tempo real
- Uso de **CEP (Complex Event Processing)** para detectar padrões de eventos e executar decisões automáticas
- **Heterogeneidade** de formatos (ex: FIX, Reuters) requer conversores de protocolo
- Arquitetura orientada a eventos, diferente do modelo cliente-servidor tradicional

---

## 3. Tendências que Impulsionam os Sistemas Distribuídos

### 3.1 Interligação em Rede Pervasiva

A Internet moderna conecta dispositivos de qualquer lugar, a qualquer momento. Inclui WiFi, Bluetooth, 3G/4G/5G, satélites. O resultado é que a conectividade deixou de ser exceção e tornou-se a norma.

**Conceitos importantes:**
- **Intranet:** rede privada organizacional protegida por firewall
- **Firewall:** filtra mensagens de entrada e saída para proteger a intranet
- **Backbone:** enlaces de alta capacidade (fibra óptica, satélite) que interligam intranets

### 3.2 Computação Móvel e Ubíqua

| Conceito | Definição |
|---|---|
| **Computação móvel** | Execução de tarefas enquanto o usuário se desloca, com acesso a recursos remotos por dispositivos portáteis |
| **Computação ubíqua (pervasiva)** | Dispositivos computacionais pequenos e baratos embutidos no ambiente físico do usuário, tornando-se parte transparente do cotidiano |

**Desafios específicos:** conectividade variável, desconexão, descoberta de serviço, operação conjunta espontânea entre dispositivos.

### 3.3 Sistemas Multimídia Distribuídos

Sistemas distribuídos devem suportar tipos de mídia contínuos (áudio, vídeo), cujo funcionamento correto depende da **preservação de relações temporais** entre os elementos (ex: taxa de quadros por segundo).

Requisitos técnicos:
- Suporte a múltiplos formatos de codificação (MPEG, MP3, HDTV)
- Garantias de **qualidade de serviço (QoS)**
- Políticas de gerenciamento de recursos e adaptação

### 3.4 Computação em Nuvem

> **Computação em nuvem** é a visão da computação como um **serviço público**: recursos de armazenamento, processamento e software disponibilizados via Internet, pagos por uso, sem necessidade de possuir a infraestrutura.

**Modelos de recurso:**
- Recursos físicos: armazenamento e processamento como commodity (ex: Amazon AWS)
- Serviços de software: aplicativos acessados pela Internet (ex: Google Apps)

**Tecnologia base:** clusters de computadores (hardware de prateleira rodando Linux), servidores blade, virtualização de sistema operacional.

**Relação com computação em grade (grid):** a computação em grade é precursora da nuvem, voltada principalmente para aplicações científicas de alto desempenho.

---

## 4. Compartilhamento de Recursos e Modelo Cliente-Servidor

### 4.1 Por que Compartilhar Recursos?

O **compartilhamento de recursos** é a principal motivação para construir sistemas distribuídos. Recursos incluem:

- Hardware: impressoras, discos, processadores
- Software/dados: arquivos, bancos de dados, mecanismos de busca
- Serviços: processamento de pagamentos, autenticação, streaming

### 4.2 Serviços

> **Serviço** é uma parte distinta de um sistema computacional que gerencia um conjunto de recursos relacionados e apresenta sua funcionalidade por meio de um conjunto de operações bem definidas.

Exemplos: serviço de arquivos (leitura/escrita/exclusão), serviço de impressão, serviço de pagamento eletrônico.

### 4.3 Modelo Cliente-Servidor

```
[Cliente] ──── requisição ────► [Servidor]
[Cliente] ◄─── resposta   ──── [Servidor]
```

| Papel | Característica |
|---|---|
| **Cliente** | Processo ativo que faz pedidos; existe enquanto o aplicativo estiver ativo |
| **Servidor** | Processo passivo que aceita e responde a pedidos; funciona continuamente |

> **Atenção:** cliente e servidor se referem a **processos**, não a máquinas físicas. O mesmo processo pode ser cliente e servidor ao mesmo tempo, dependendo da operação.

---

## 5. Os Oito Desafios dos Sistemas Distribuídos

### 5.1 Heterogeneidade

Sistemas distribuídos integram componentes com diferenças em:
- Redes (WiFi, Ethernet, 4G)
- Hardware (arquiteturas de CPU diferentes — big-endian vs. little-endian)
- Sistemas operacionais (Linux, Windows — APIs diferentes para sockets)
- Linguagens de programação (representações diferentes de tipos e estruturas)
- Implementações de diferentes desenvolvedores

**Solução principal: Middleware**

> **Middleware** é uma camada de software que fornece uma abstração de programação e mascara a heterogeneidade subjacente.

Exemplos: CORBA, Java RMI, serviços Web.

**Código móvel:** código que pode ser transferido entre computadores e executado no destino (ex: applets Java, JavaScript). A **máquina virtual (JVM)** é a estratégia que permite portabilidade de código entre plataformas heterogêneas.

---

### 5.2 Sistemas Abertos

> Um sistema distribuído é **aberto** quando pode ser estendido e reimplementado de várias formas, com novas funcionalidades sendo adicionadas sem quebrar as existentes.

**Requisito fundamental:** publicação das interfaces dos componentes (documentação pública).

Mecanismos de publicação:
- **RFCs (Requests for Comments):** documentos técnicos que especificam os protocolos da Internet
- **W3C:** define e publica padrões para a Web

**Características de sistemas distribuídos abertos:**
- Interfaces principais são publicadas
- Baseados em mecanismo de comunicação uniforme
- Construídos com hardware e software heterogêneo de diferentes fornecedores
- Independentes de fornecedores específicos

---

### 5.3 Segurança

A segurança de recursos de informação tem três dimensões:

| Dimensão | Definição |
|---|---|
| **Confidencialidade** | Proteção contra exposição para pessoas não autorizadas |
| **Integridade** | Proteção contra alteração ou dano não autorizado |
| **Disponibilidade** | Proteção contra interferência com os meios de acesso |

**Desafios ainda não totalmente resolvidos:**

- **Ataque de Negação de Serviço (DoS):** bombardeio com pedidos sem sentido para tornar o serviço inacessível
- **Segurança de código móvel:** código baixado pode ter comportamento imprevisível e malicioso

**Solução principal:** técnicas de criptografia para proteção de conteúdo das mensagens e para autenticação de identidade.

---

### 5.4 Escalabilidade

> Um sistema é **escalável** se permanece eficiente quando há aumento significativo no número de recursos e usuários.

**Quatro desafios para escalar:**

| Desafio | Descrição | Exemplo |
|---|---|---|
| **Custo dos recursos físicos** | Para n usuários, recursos físicos devem crescer em O(n) | Adicionar servidores de arquivos conforme cresce o número de usuários |
| **Perda de desempenho** | Acesso a estruturas hierárquicas cresce em O(log n) — aceitável | DNS usa hierarquia de nomes |
| **Recursos de software esgotados** | Espaço de endereçamento pode se esgotar | IPv4 com 32 bits → substituição por IPv6 com 128 bits |
| **Gargalos de desempenho** | Algoritmos centralizados se tornam gargalo em grande escala | Tabela central de nomes → DNS distribuído e hierárquico |

**Técnicas de escalabilidade:** replicação de dados, cache, distribuição de servidores.

---

### 5.5 Tratamento de Falhas

Em sistemas distribuídos, as falhas são **parciais**: alguns componentes falham enquanto outros continuam operando. Isso torna o tratamento de falhas muito mais complexo do que em sistemas centralizados.

**Cinco técnicas de tratamento de falhas:**

| Técnica | Descrição |
|---|---|
| **Detecção** | Identificar que uma falha ocorreu (checksums, timeouts) |
| **Mascaramento** | Ocultar ou atenuar a falha (retransmissão de mensagens, gravação em dois discos) |
| **Tolerância** | Projetar clientes e serviços para funcionar mesmo diante de falhas (ex: browser informa o usuário em vez de travar) |
| **Recuperação** | Restaurar dados persistentes ao estado consistente após falha de servidor |
| **Redundância** | Usar componentes redundantes para garantir disponibilidade (múltiplas rotas, DNS replicado, bancos de dados replicados) |

> **Disponibilidade** = proporção de tempo em que o sistema está pronto para uso. Falhas parciais permitem que usuários migrem para outros nós disponíveis.

---

### 5.6 Concorrência

Múltiplos clientes podem tentar acessar o mesmo recurso simultaneamente. Sem controle, operações concorrentes podem produzir resultados inconsistentes (condição de corrida).

**Exemplo clássico:** dois lances em um leilão processados concorrentemente sem sincronização → valores podem ser misturados.

**Solução:** sincronização das operações sobre recursos compartilhados via semáforos, monitores ou outros mecanismos de exclusão mútua.

---

### 5.7 Transparência

> **Transparência** é a ocultação, para o usuário final ou programador de aplicativos, da separação dos componentes, de modo que o sistema seja percebido como um todo.

**As 8 formas de transparência (ANSA/RM-ODP):**

| Tipo | O que oculta |
|---|---|
| **Acesso** | Diferença entre acesso local e remoto (mesmas operações para ambos) |
| **Localização** | Localização física ou de rede do recurso |
| **Concorrência** | Uso simultâneo por múltiplos processos sem interferência |
| **Replicação** | Existência de múltiplas cópias do recurso |
| **Falhas** | Falhas de componentes de hardware ou software |
| **Mobilidade** | Movimentação de recursos e clientes dentro do sistema |
| **Desempenho** | Reconfiguração do sistema para manter desempenho conforme a carga varia |
| **Escalabilidade** | Expansão do sistema sem alteração de estrutura ou algoritmos |

> As mais importantes são **transparência de acesso** e **transparência de localização** — juntas formam a **transparência de rede**.

**Exemplo:** endereço de e-mail `usuario@empresa.com` oferece transparência de localização e de acesso — o remetente não precisa saber onde fisicamente o destinatário está.

---

### 5.8 Qualidade de Serviço (QoS)

Além de fornecer funcionalidade, um sistema distribuído deve oferecer **garantias de qualidade** no acesso aos serviços:

- **Confiabilidade:** o serviço funciona corretamente
- **Segurança:** proteção contra acessos indevidos
- **Desempenho:** tempo de resposta e throughput adequados
- **Pontualidade:** dados críticos (ex: vídeo ao vivo) devem ser entregues dentro de prazos estritos

> **QoS** implica reserva garantida de recursos de computação e comunicação para que aplicações com requisitos temporais estritos possam ser atendidas. Pedidos que não podem ser atendidos devem ser rejeitados.

---

## 6. Estudo de Caso: A World Wide Web

A Web é um sistema distribuído aberto de grande escala, baseado em três componentes tecnológicos:

### 6.1 HTML (HyperText Markup Language)
Linguagem de marcação para especificar o conteúdo, leiaute e links de páginas Web. Interpretada exclusivamente pelo navegador (cliente).

### 6.2 URL (Uniform Resource Locator)
Identificador único de recursos na Web. Estrutura de um URL HTTP:

```
http:// nomedoservidor [:porta] [/nomeDeCaminho] [?consulta] [#fragmento]
```

| Componente | Exemplo | Função |
|---|---|---|
| Servidor | `www.google.com` | Identifica o servidor (nome DNS) |
| Caminho | `/search` | Localiza o recurso no servidor |
| Consulta | `?q=obama` | Parâmetros para o recurso (formulários, buscas) |
| Fragmento | `#conformance` | Identificador de seção dentro do recurso |

**URLs proporcionam transparência de localização** (o nome DNS abstrai o endereço IP), mas **não transparência de mobilidade** (ao mudar de domínio, os links ficam inválidos).

### 6.3 HTTP (HyperText Transfer Protocol)
Protocolo requisição-resposta que define a interação entre clientes e servidores Web.

**Características principais:**
- **Métodos:** GET (recuperar dados), POST (enviar dados), PUT (criar recurso), DELETE (excluir recurso)
- **Tipos MIME:** identificam o tipo de conteúdo retornado (text/html, image/GIF, application/zip)
- **Um recurso por requisição:** uma página com 9 imagens gera 10 requisições separadas
- **Controle de acesso simplificado:** qualquer cliente pode acessar recursos públicos; restrições exigem autenticação

### 6.4 Páginas Dinâmicas e CGI
URLs podem designar **programas** no servidor, não apenas arquivos. O programa CGI (Common Gateway Interface) processa a entrada do usuário e gera HTML dinamicamente como resposta.

### 6.5 JavaScript, AJAX e Applets
Permitem que código seja executado **no cliente (navegador)**:
- **JavaScript:** validação de formulários, atualização parcial de páginas
- **AJAX:** atualização assíncrona de partes da página sem recarregar o todo
- **Applets Java:** aplicativos completos executados no navegador

### 6.6 Serviços Web e REST
A arquitetura **REST (REpresentational State Transfer)** usa os métodos HTTP como interface de operações sobre recursos identificados por URL. Permite integração entre programas (não apenas navegadores) por meio de dados em XML ou JSON.

### 6.7 Problemas da Web como Sistema Distribuído
- **Links pendentes:** recursos excluídos deixam referências quebradas
- **Escalabilidade:** servidores populares sofrem com volume de acessos → solução: cache e servidores proxy
- **Busca imprecisa:** mecanismos de busca por palavras são limitados → solução em desenvolvimento: Web semântica (metadados RDF)

---

## 7. Síntese — Mapa Conceitual do Capítulo

```
SISTEMA DISTRIBUÍDO
├── Definição: componentes em rede que se coordenam por mensagens
├── Características: concorrência | sem relógio global | falhas independentes
├── Motivação: compartilhamento de recursos
│   └── Modelo: cliente ──requisição──► servidor
├── Exemplos: Web search | MMOGs | sistemas financeiros
├── Tendências: redes pervasivas | computação móvel | nuvem
└── Desafios (8):
    ├── Heterogeneidade → Middleware
    ├── Sistemas abertos → interfaces publicadas (RFCs, W3C)
    ├── Segurança → criptografia; problemas: DoS, código móvel
    ├── Escalabilidade → replicação, cache, hierarquia, descentralização
    ├── Tratamento de falhas → detecção, mascaramento, tolerância, recuperação, redundância
    ├── Concorrência → sincronização (semáforos)
    ├── Transparência → 8 tipos (acesso e localização: as mais importantes)
    └── Qualidade de serviço → garantias de desempenho, pontualidade
```

---

## 8. Erros Comuns dos Alunos

| Equívoco | Correção |
|---|---|
| Confundir "sistema distribuído" com "sistema paralelo" | SD: componentes em máquinas diferentes conectadas por rede; sistema paralelo: múltiplos processadores na mesma máquina |
| Acreditar que existe um relógio global preciso na Internet | Não existe; sincronização tem limite de precisão; algoritmos especiais (cap. 14) são necessários |
| Pensar que falha de um nó derruba o sistema inteiro | Falhas são parciais; outros nós continuam operando — o desafio é lidar com isso |
| Confundir middleware com sistema operacional | Middleware é uma camada extra que abstrai heterogeneidade; não substitui o SO |
| Achar que "sistema aberto" significa "sem segurança" | Sistema aberto = interfaces publicadas e extensíveis; segurança é tratada separadamente |
| Confundir transparência com invisibilidade total | Transparência é parcial e intencional; algumas informações devem estar disponíveis para o programador |

---

## 9. Questões para Revisão e Discussão

1. Quais são as três características que decorrem diretamente da definição de sistema distribuído? Explique cada uma com um exemplo real.

2. Por que a inexistência de relógio global é um problema para sistemas distribuídos? Cite uma situação prática em que isso pode causar inconsistência.

3. Compare as três arquiteturas discutidas para MMOGs (cliente-servidor centralizado, servidores particionados, peer-to-peer) em termos de escalabilidade, consistência e complexidade de implementação.

4. Explique o papel do middleware no enfrentamento da heterogeneidade. Cite dois exemplos de middleware e o que eles abstraem.

5. Um sistema distribuído com 1000 usuários deve funcionar de forma tão eficiente quanto com 10 usuários. Que técnicas o Coulouris recomenda para garantir escalabilidade?

6. Qual a diferença entre mascaramento de falhas e tolerância a falhas? Dê um exemplo de cada técnica.

7. Entre as 8 formas de transparência, qual você considera mais difícil de implementar e por quê?

8. Como a arquitetura da Web demonstra os conceitos de sistema aberto, compartilhamento de recursos e modelo cliente-servidor?

---

## Referência

COULOURIS, G. et al. **Sistemas Distribuídos: Conceitos e Projeto**. 5. ed. Porto Alegre: Bookman, 2013. Capítulo 1, p. 1–34.
