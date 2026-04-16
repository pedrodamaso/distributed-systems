# Capítulo 10 — Sistemas Peer-to-Peer
## Material Teórico para Sistemas Distribuídos

> **Livro-base:** Coulouris et al., *Sistemas Distribuídos: Conceitos e Projeto*, 5ª ed., Bookman, 2013  
> **Capítulo:** 10 — Peer-to-Peer Systems (pp. 423–461)

---

## Objetivos de Aprendizagem

Ao final deste capítulo, o aluno deverá ser capaz de:

1. Explicar o paradigma P2P e suas diferenças em relação ao modelo cliente-servidor
2. Descrever as três gerações de sistemas P2P e as lições do Napster
3. Enunciar os requisitos funcionais e não funcionais de middleware P2P
4. Explicar o conceito de sobreposição de roteamento (routing overlay) e as diferenças entre DHT e DOLR
5. Descrever o algoritmo de roteamento do Pastry (conjuntos de folhas + tabela de prefixos)
6. Comparar sistemas P2P estruturados e não estruturados, com as estratégias de busca em não estruturados
7. Analisar os estudos de caso Squirrel, OceanStore e Ivy com seus trade-offs de desempenho/segurança

---

## Pré-requisitos

| Conceito | Onde revisar |
|---|---|
| Roteamento IP e CIDR | Capítulo 3 (Seção 3.4.3) |
| Funções de resumo seguro (SHA-1) | Capítulo 11 (Seção 11.4.3) |
| Tolerância a falhas Bizantinas | Capítulo 18 |
| Copy-on-write e regiões de memória | Capítulo 7 (Seção 7.4.2) |
| Vetores de versão (carimbos vetoriais) | Capítulo 14 (Seção 14.4) |

---

## 1. Introdução: O Paradigma Peer-to-Peer

### 1.1 Definição e Características

Sistemas P2P exploram recursos disponíveis **nos limites da Internet** — armazenamento, ciclos de processamento, conteúdo e presença humana (definição de Shirky, 2000).

**Características fundamentais:**
- Cada nó **contribui** com recursos para o sistema
- Todos os nós têm as mesmas capacidades e responsabilidades funcionais
- O funcionamento correto não depende de sistemas administrados centralmente
- Possibilidade de anonimato limitado para provedores e usuários

### 1.2 Três Gerações de Sistemas P2P

| Geração | Sistemas | Característica principal |
|---|---|---|
| **1ª** | Napster (1999) | Índice centralizado + arquivos distribuídos |
| **2ª** | Gnutella, Freenet, Kazaa, BitTorrent | Maior escalabilidade, anonimato e tolerância a falhas; índices distribuídos mas específicos por sistema |
| **3ª** | Pastry, Tapestry, CAN, Chord, Kademlia | **Middleware genérico e independente de aplicação**; garante entrega em O(log N) passos |

### 1.3 Sobreposição de Roteamento vs. Roteamento IP

| Aspecto | Roteamento IP | Sobreposição P2P |
|---|---|---|
| **Escala** | IPv4: 2³² nós; estrutura hierárquica pré-alocada | Espaço de nomes muito maior (>2¹²⁸), plano e aleatório |
| **Balanceamento** | Determinado pela topologia e tráfego vigente | Objetos posicionados aleatoriamente, independente da topologia |
| **Dinâmica** | Tabelas atualizadas com atraso da ordem de 1 hora | Atualizações em frações de segundo |
| **Tolerância a falhas** | Redundância projetada manualmente na rede | Replicação com fator n → tolerância de n falhas de nós |
| **Destino** | Exatamente um nó por endereço | Pode direcionar para a réplica mais próxima disponível |
| **Segurança** | Seguro apenas se todos confiam; sem anonimato | Segurança possível em confiança limitada; anonimato parcial |

---

## 2. Napster e Seu Legado

### 2.1 Arquitetura

```
                      Servidores Napster
                    (Índice replicado centralizado)
                          /          \
          1. Req. localização       5. Atualização índice
                        /                \
               Cliente A              Cliente B
                   |        3. Req.        |
                   +---- arquivo -----→    |
                   |     4. arquivo ←------+
                   |       2. lista de peers
```

**Fluxo de operação:**
1. Cliente solicita localização de arquivo ao servidor de índice
2. Servidor retorna lista de peers que oferecem o arquivo
3. Cliente requisita diretamente o arquivo a um peer
4. Peer envia o arquivo
5. Cliente atualiza o índice com seus próprios arquivos disponíveis

### 2.2 Lições do Napster

**Demonstrações positivas:**
- Viabilidade de serviço de larga escala usando recursos de usuários comuns
- Distribuição de carga por localidade de rede (minimizar nós intermediários)

**Limitações:**
- Índice unificado centralizado = **gargalo** e ponto único de falha
- Funciona bem apenas para arquivos imutáveis (música nunca atualizada)
- Sem garantias de disponibilidade de arquivos individuais
- Índice centralizado tornou operadores legalmente rastreáveis → ação judicial fatal

---

## 3. Requisitos do Middleware Peer-to-Peer

### 3.1 Requisitos Funcionais

- Localizar e comunicar com **qualquer recurso** da rede
- Adicionar/remover recursos e máquinas a qualquer momento
- API de programação simples, independente do tipo de recurso

### 3.2 Requisitos Não Funcionais

| Requisito | Descrição |
|---|---|
| **Escalabilidade global** | Suportar milhões de objetos em centenas de milhares de nós |
| **Balanceamento de carga** | Posicionamento aleatório + replicação de recursos populares |
| **Otimização de localidade** | Reduzir latência colocando recursos próximos de quem os acessa |
| **Disponibilidade dinâmica** | Acomodar nós que entram/saem a qualquer momento (sessão média: 135 min no Overnet) |
| **Segurança em confiança heterogênea** | Autenticação + criptografia mesmo com nós não confiáveis |
| **Anonimato e negação plausível** | Proteger identidade de provedores e usuários de dados |

**Dado empírico:** No sistema Overnet (85.000 nós), duração média de sessão foi de 135 min (mediana: 79 min). Na rede corporativa da Microsoft: 37,7 horas. A disparidade reflete diferenças entre usuários domésticos e corporativos.

---

## 4. Sobreposição de Roteamento (Routing Overlay)

### 4.1 Conceito Central

A sobreposição de roteamento é uma **camada de aplicação** completamente separada do roteamento IP, responsável por:

- **Roteamento de requisições**: direcionar a requisição de um cliente ao nó que contém a réplica do objeto
- **Inserção de objetos**: tornar novos objetos acessíveis a todos
- **Remoção de objetos**: tornar objetos indisponíveis quando solicitado
- **Adição/remoção de nós**: redistribuir responsabilidades quando nós entram ou saem

### 4.2 GUID — Globally Unique Identifier

O GUID é calculado aplicando uma **função de resumo segura** (SHA-1) sobre:
- O estado do objeto (para objetos imutáveis — garante autenticidade)
- A chave pública do nó (para nós)
- O nome do arquivo (para objetos mutáveis)

**Propriedades dos GUIDs:**
- Distribuídos aleatoriamente no intervalo [0, 2¹²⁸-1]
- São **nomes puros** (opacos) — não contêm informação de endereçamento
- Colisões extremamente improváveis
- Objetos imutáveis: GUID = prova de autenticidade (any change = different GUID)

### 4.3 Interface DHT (Distributed Hash Table)

```python
# API DHT — conforme implementada pelo PAST sobre Pastry

put(GUID, dados)
# Armazena dados em réplicas em todos os nós responsáveis pelo GUID.
# A camada DHT escolhe a localização, armazena e replica.

remove(GUID)
# Exclui todas as referências e dados associados ao GUID.

value = get(GUID)
# Recupera os dados associados ao GUID de um dos nós responsáveis.
```

**Modelo DHT:** um item com GUID X é armazenado no nó cujo GUID é numericamente mais próximo a X, **e** nos r nós vizinhos (r = fator de replicação, tipicamente até 16).

### 4.4 Interface DOLR (Distributed Object Location and Routing)

```python
# API DOLR — conforme implementada pelo Tapestry

publish(GUID)
# O nó que contém o objeto anuncia sua existência.
# Os objetos podem estar em qualquer lugar — o DOLR mantém o mapeamento GUID → IP.

unpublish(GUID)
# Torna o objeto inacessível.

sendToObj(msg, GUID, [n])
# Envia mensagem ao objeto identificado pelo GUID.
# Parâmetro opcional [n]: envia para n réplicas simultaneamente.
```

**Diferença DHT × DOLR:** No DHT, o middleware decide onde armazenar; no DOLR, a aplicação decide onde colocar as réplicas e publica os mapeamentos.

### 4.5 Métricas de Distância nos Principais Sistemas

| Sistema | Métrica de distância |
|---|---|
| **Pastry, Tapestry** | Comprimento do prefixo hexadecimal comum |
| **Chord** | Diferença numérica entre GUIDs (anel circular) |
| **CAN** | Distância euclidiana em hiperespaço d-dimensional |
| **Kademlia** | XOR entre GUIDs (simétrico → tabelas mais simples) |

---

## 5. Pastry — Estudo de Caso Detalhado

### 5.1 Visão Geral

- **GUIDs de 128 bits**, gerados via SHA-1 da chave pública (nós) ou do conteúdo/nome (objetos)
- Roteamento correto em **O(log N)** passos para N nós participantes
- Se o GUID não existe como nó ativo, a mensagem é entregue ao nó ativo **numericamente mais próximo**
- Protótipo: FreePastry; versão aprimorada: **MSPastry** (com mecanismos de dependabilidade)

### 5.2 Estrutura de Dados em Cada Nó

Cada nó Pastry mantém:

1. **Conjunto de folhas (leaf set) L** — vetor de tamanho 2l contendo GUIDs e IPs dos l nós vizinhos acima e l abaixo no espaço de GUIDs (tipicamente l = 8)
2. **Tabela de roteamento R** — estruturada por prefixos hexadecimais, com 32 linhas × 15 colunas
3. **Conjunto de vizinhança** — nós próximos em distância de rede real (usado para localidade)

### 5.3 Tabela de Roteamento (Estrutura por Prefixo)

Para um nó com GUID começando com `65A1`:

```
Linha 0 (p=0): cobre GUIDs com 1º dígito 0,1,2,...,9,A,B,C,D,E,F (exceto 6)
               [n₀, n₁, n₂, n₃, n₄, n₅, _65A1_, n₇, n₈, n₉, nA, nB, nC, nD, nE, nF]
                                           ↑ entrada "self" — sombreada
Linha 1 (p=1): cobre GUIDs iniciando com 60,61,62,...,69,6A,...,6F (exceto 65)
               [n₆₀, n₆₁, n₆₂, n₆₃, n₆₄, _65A1_, n₆₆, n₆₇, n₆₈, n₆₉, n₆A, n₆B, n₆C, n₆F, n₆E]

Linha 2 (p=2): cobre GUIDs iniciando com 650,651,...,659,65A,...,65F (exceto 65A)
Linha 3 (p=3): cobre GUIDs iniciando com 65A0,65A1,...,65AF (exceto 65A1)
...
```

**Propriedade:** A linha p contém nós cujos GUIDs têm exatamente p dígitos iniciais em comum com o nó corrente.

### 5.4 Algoritmo de Roteamento (Figura 10.9)

```
Para encaminhar mensagem M ao destino D (nó corrente = A, tabela = R, leaf set = L):

1. SE (L₋ₗ ≤ D ≤ Lₗ) ENTÃO          // D está no intervalo do leaf set
2.     Encaminha M para o nó de L (ou A) com GUID mais próximo a D
3. SENÃO                               // Usa tabela de roteamento
4.     p ← comprimento do prefixo comum mais longo de D e A
       i ← (p+1)-ésimo dígito hexadecimal de D
5.     SE R[p,i] ≠ null ENTÃO
           Encaminha M para R[p,i]    // Nó com prefixo p+1 comum com D
6.     SENÃO                          // Entrada ausente (nó falhou)
7.         Encaminha M para qualquer nó em L ou R com prefixo p,
           mas GUID numericamente mais próximo a D
```

**Garantia:** A cada passo, a mensagem é encaminhada para um nó com GUID numericamente mais próximo ao destino → convergência garantida.

### 5.5 Integração de Novos Nós

Suponha novo nó X com GUID X:
1. X calcula GUID via SHA-1(chave_pública_X)
2. X contata um nó vizinho A (por distância de rede)
3. X envia mensagem **join** com destino = X; Pastry roteia normalmente até Z (nó mais próximo a X)
4. Todos os nós A, B, C,... no caminho A→Z enviam suas tabelas de roteamento para X
5. X constrói sua tabela: linha 0 de A, linha 1 de B (mesmo 1º dígito), linha 2 de C (mesmo 1º e 2º dígito)...
6. X usa leaf set de Z como aproximação inicial (difere em apenas 1 membro)
7. X notifica todos os nós de seus conjuntos → eles atualizam suas tabelas
8. Custo total: **O(log N) mensagens**

### 5.6 Tolerância a Falhas

| Mecanismo | Função |
|---|---|
| **Pulsações (heartbeats)** | Cada nó envia heartbeat ao vizinho esquerdo; detecta falhas |
| **Reparo do leaf set** | Ao detectar falha, solicita leaf set de nó vizinho ativo para substituição |
| **Reparo da tabela** | Entradas suspeitas substituídas por alternativas de nós vizinhos |
| **Protocolo gossip** | Troca de tabelas de roteamento entre nós a cada ~20 min |
| **Aleatoriedade no roteamento** | Pequena proporção de saltos usa prefixo menor que máximo → tolerância a nós mal-intencionados |
| **Confirmações por salto (MSPastry)** | Cada hop confirma recepção; timeout → rota alternativa |

### 5.7 Localidade: Proximity Neighbour Selection (PNS)

Ao construir a tabela de roteamento, para cada posição existem múltiplas candidatas. O PNS seleciona o **nó mais próximo em latência de rede** disponível.

**Resultado:** Rotas em média apenas 30–50% mais longas que o ótimo teórico.

### 5.8 Avaliação de Desempenho (MSPastry)

| Métrica | Resultado |
|---|---|
| Mensagens perdidas (perda IP 0%) | 1,5 em 100.000 |
| Mensagens perdidas (perda IP 5%) | 3,3 em 100.000 |
| RDP (Relative Delay Penalty) — 0% perda | ~1,8× (overhead da sobreposição vs UDP direto) |
| RDP — 5% perda | ~2,2× |
| Tráfego de controle | < 2 mensagens/min/nó |

---

## 6. Tapestry — Sobreposição com API DOLR

- **Identificadores de 160 bits** (NodeIds para nós, GUIDs para objetos)
- Implementa roteamento por prefixo similar ao Pastry, mas expõe API DOLR
- Para cada GUID G existe um **nó-raiz R_G** (numericamente mais próximo a G)
- Nós que contêm réplicas chamam `publish(G)` periodicamente → mensagem roteada até R_G
- **Caching no caminho de publicação**: cada nó intermediário armazena mapeamento (G, IP_nó_origem)
- Para múltiplas réplicas com mesmo GUID: mapeamentos ordenados por distância de rede → requisições vão para a réplica mais próxima

```
Exemplo (Figura 10.10):
- Arquivo "Livros de Phil" tem GUID G=4378
- Réplicas em nós 4228 e AA93
- Nó raiz R_G = 4377 (numericamente mais próximo a 4378)
- Mensagem sendTo(4378) segue: E791 → 57EC → 4664 → 4B4F → AA93 (réplica mais próxima)
```

---

## 7. Estruturado vs. Não Estruturado

### 7.1 Comparação

| Aspecto | P2P Estruturado | P2P Não Estruturado |
|---|---|---|
| Topologia | Controlada globalmente (DHT, anel) | Ad hoc, regras locais |
| Garantia de localização | Sim, em O(log N) | Não — probabilístico |
| Overhead de mensagens | Moderado e previsível | Pode inundar a rede |
| Manutenção | Estruturas complexas, custo em ambientes dinâmicos | Auto-organizado, resiliente |
| Exemplos | Pastry, Tapestry, CAN, Chord | Gnutella, FreeNet, BitTorrent |

### 7.2 Estratégias de Busca em Sistemas Não Estruturados

| Estratégia | Mecanismo | Quando usar |
|---|---|---|
| **Inundação** (Gnutella 0.4) | Encaminha para todos os vizinhos com TTL | Simples, mas não escala |
| **Pesquisa em anel expandida** | Série de buscas com TTL crescente | Quando muitas requisições são satisfeitas localmente |
| **Caminhadas aleatórias** | Múltiplos caminhantes seguindo trajetos aleatórios | Baixo overhead, convergência probabilística |
| **Gossip/Epidêmico** | Propaga com probabilidade p para cada vizinho | Disseminação ampla com overhead controlável |

### 7.3 Gnutella 0.6 — Arquitetura Híbrida

**Problema do Gnutella 0.4:** inundação pura, conectividade média 5 vizinhos/nó → não escala.

**Melhorias do Gnutella 0.6:**

```
Arquitetura:
                    Ultrapar A ←→ Ultrapar B ←→ Ultrapar C
                   /    ↑              ↑             ↑
                  /     |              |             |
        Folha 1  2    Folhas 3,4    Folhas 5,6    Folha 7
```

1. **Ultrapares:** nós com recursos adicionais, eleitos como backbone da rede (>32 conexões entre ultrapares)
2. **Nós folha:** conectam-se a um pequeno número de ultrapares
3. **QRP (Query Routing Protocol):**
   - Cada nó folha produz uma **QRT (Query Routing Table)**: resumo hash das palavras nos nomes de arquivos
   - Ex.: "Capítulo 10 sobre P2P" → {65, 47, 09, 76}
   - Ultrapares fazem a **união** das QRTs de todas as folhas conectadas
   - Consultas são encaminhadas apenas para caminhos com correspondência na QRT
   - Resultado: redução drástica de tráfego desnecessário
4. **Resposta direta:** uma vez encontrado um arquivo, é enviado diretamente via UDP ao ultrapar iniciador

---

## 8. Estudos de Caso: Aplicações

### 8.1 Squirrel — Cache Web Peer-to-Peer (sobre Pastry)

**Objetivo:** substituir cache Web proxy centralizada por uma distribuída nos próprios desktops da rede local.

**Mecanismo:**
```
1. Nó cliente recebe GET para URL
2. SHA-1(URL) → GUID de 128 bits
3. GUID identifica o "nó de base" (numericamente mais próximo)
4. Pastry roteia requisição até o nó de base
5. Se cache válida → retorna objeto
6. Se cache inválida/ausente → nó de base busca no servidor de origem
```

**Avaliação (simulação usando cargas reais da Microsoft):**

| Métrica | Cache centralizada | Squirrel (100MB/nó) |
|---|---|---|
| Taxa de acertos — Redmond (36k clientes) | 29% | 28% |
| Taxa de acertos — Cambridge (105 clientes) | 38% | 37% |
| Saltos médios de roteamento (Redmond) | 1 (direto) | 4,11 |
| Carga por nó (requisições recebidas) | N/A | 0,31/min |

**Conclusão:** desempenho comparável à cache centralizada; overhead nos nós é imperceptível.

### 8.2 OceanStore — Armazenamento P2P com Objetos Mutáveis (sobre Tapestry)

**Objetivo:** armazenamento persistente de larga escala, com tolerância a falhas, para objetos mutáveis.

**Organização do armazenamento (versioning):**

```
Objeto "arquivo.txt"
        ↓ AGUID (permanente — identifica todas as versões)
  Certificado (assinado) → VGUID da versão corrente
        ↓ VGUID (versão i)
    Bloco-raiz (metadados) → blocos de dados + VGUID da versão i-1
        ↓↓↓↓
   d1 d2 d3 d4 d5 (BGUIDs — imutáveis, calculados do conteúdo)

   Versão i+1 atualiza apenas d1, d2, d3 → compartilha d4, d5 (copy-on-write)
```

**Três tipos de identificadores:**

| Tipo | Significado | Base de cálculo |
|---|---|---|
| **BGUID** | GUID do bloco | SHA-1 do conteúdo do bloco (imutável) |
| **VGUID** | GUID da versão | BGUID do bloco-raiz da versão |
| **AGUID** | GUID ativo | SHA-1(nome_arquivo ‖ chave_pública_proprietário) |

**Mecanismo de confiança — Anel Interno:**
- Pequeno conjunto de nós designados para cada objeto
- Atualizações exigem **acordo de consenso Bizantino** (algoritmo de Castro e Liskov)
- Custo O(n²) → anel interno mantido pequeno; resultado replicado em cópias secundárias via Tapestry

**Erasure Coding (Código de Obliteração):**
```
m = 16 fragmentos originais → codificados em n = 32 fragmentos
Propriedade: qualquer m fragmentos reconstroem o bloco original
Tolerância: perda de até n-m = 16 nós sem perda de dados
Custo: 2× o armazenamento
```

**Avaliação (benchmark Andrew — Pond):**

| Fase | NFS local | Pond local | NFS remoto | Pond remoto |
|---|---|---|---|---|
| 1 (criar dirs) | 0,0s | 1,9s | 0,9s | 2,8s |
| 2 (copiar árvore) | 0,3s | 11,0s | 9,4s | 16,8s |
| 3 (stat arquivos) | 1,1s | 1,8s | 8,3s | 1,8s |
| 4 (ler bytes) | 0,5s | 1,5s | 6,9s | 1,5s |
| 5 (compilar) | 2,6s | 21,0s | 21,5s | 32,0s |
| **Total** | **4,5s** | **37,2s** | **47,0s** | **54,9s** |

**Conclusão:** competitivo com NFS sobre WAN para leitura; inadeguado para LAN; custo da criptografia (chaves 512 bits) é significativo.

### 8.3 Ivy — Sistema de Arquivos P2P com Logs (sobre DHash)

**Objetivo:** sistema de arquivos com API NFS-like, seguro em ambiente de confiança parcial.

**Arquitetura:**
```
Aplicação NFS
     ↓
Módulo cliente NFS modificado
     ↓
Servidor Ivy (por nó — autônomo)
     ↓
DHash (Distributed Hash Store — SHA-1 keyed)
     ↓
Múltiplos nós DHash na LAN ou Internet
```

**Estrutura de armazenamento:**
- Cada participante mantém um **log append-only** separado das suas atualizações
- Registros de log: imutáveis, endereçados por SHA-1 do conteúdo
- **Cabeçalho de log**: bloco mutável assinado com chave privada; aponta para entrada mais recente
- **Vetores de versão**: ordenam updates de múltiplos participantes (relógio global não assumido)

**Consistência fechar-para-abrir (close-to-open):**
- Writes locais acumulam até `close()` do arquivo
- Operações write são persistidas como **único registro de log** ao fechar
- Outros processos veem a atualização apenas após o close

**Segurança e tolerância a mal-intencionados:**
- Registros de log: imutáveis → autenticados pelo GUID
- Cabeçalho de log: assinado com chave privada do participante
- **Modo de visualização (view mode)**: representação do sistema calculada a partir de um subconjunto de logs
- Participante mal-intencionado detectado → ejeitado do modo de visualização; arquivos excluídos por ele ficam visíveis novamente

**Avaliação:**
- Desempenho: 2–3× NFS (resultado adequado considerando ambiente P2P)
- Principal contribuição: modelo de segurança para confiança parcial em larga escala

---

## Mapa Conceitual

```
Sistemas Peer-to-Peer
├── Geração 1: Napster
│   └── Índice centralizado + arquivos distribuídos
│
├── Geração 2: Gnutella, Freenet, BitTorrent
│   └── Índices distribuídos específicos por sistema
│
└── Geração 3: Middleware P2P
    ├── Identificação: GUID (SHA-1 → nome puro e opaco)
    │
    ├── Sobreposição de Roteamento
    │   ├── DHT: put(GUID,data) / get(GUID)
    │   │   └── Pastry (prefixo hexadecimal + leaf set)
    │   └── DOLR: publish / sendToObj
    │       └── Tapestry (prefixo + caching no caminho)
    │
    ├── Sistemas Estruturados vs Não Estruturados
    │   ├── Estruturados: O(log N) garantido, manutenção complexa
    │   └── Não estruturados: auto-organizado, busca probabilística
    │       └── Gnutella 0.6: ultrapares + QRP
    │
    └── Aplicações
        ├── Squirrel → cache Web (taxa de acertos ≈ cache centralizada)
        ├── OceanStore → armazenamento mutável (versioning + erasure coding + BFT)
        └── Ivy → sistema de arquivos (logs por participante + view modes)
```

---

## Relevância para Sistemas de Informação

| Contexto SI | Conceito do Capítulo | Aplicação Prática |
|---|---|---|
| CDN (Content Delivery Network) | Replicação P2P + localidade | Akamai, Cloudflare replicam conteúdo próximo ao usuário |
| Blockchain/Web3 | GUID via hash, confiança sem servidor central | Bitcoin usa UTXO com hash; IPFS usa CIDs (Content IDs) baseados em hash |
| Torrents | Gnutella / BitTorrent | 43–70% do tráfego Internet era P2P (2008–2009) |
| Sistemas de armazenamento distribuído | DHT | Amazon DynamoDB usa DHT com consistent hashing |
| Kubernetes/microserviços | Service discovery P2P | Consul, etcd para descoberta de serviços |
| IPFS (InterPlanetary File System) | DHT + CIDs = conteúdo endereçável | Alternativa descentralizada à Web tradicional |
| Segurança de dados | Erasure coding | Google, Facebook usam erasure coding em data centers |
| Anonimato | Freenet, Tor | Tor usa onion routing inspirado em P2P |

---

## Erros Conceituais Comuns

1. **"Sistemas P2P são sempre totalmente descentralizados"**
   - Errado: o Napster tinha índice centralizado; o Gnutella 0.6 tem ultrapares eleitos; muitos sistemas são **híbridos**.

2. **"O GUID é como um endereço IP"**
   - Errado: GUIDs são **nomes puros e opacos** — não contêm informação sobre localização. A sobreposição de roteamento resolve o mapeamento GUID → nó.

3. **"DHT e DOLR fazem a mesma coisa"**
   - Errado: no DHT, o middleware decide onde armazenar (get/put); no DOLR, a aplicação decide onde colocar as réplicas e publica os mapeamentos (publish/sendToObj).

4. **"O Pastry sempre encontra o destino em log N saltos"**
   - Quase correto: em condições normais, sim. Quando há falhas recentes não propagadas, pode usar o Estágio I (leaf set), que é correto mas mais lento (~N/2ˡ saltos).

5. **"Sistemas P2P estruturados são superiores a não estruturados"**
   - Depende: estruturados garantem busca em O(log N), mas exigem manutenção complexa. Não estruturados dominam o compartilhamento de arquivos na prática (Gnutella, BitTorrent) por serem auto-organizados e resilientes.

6. **"O OceanStore resolve o problema de objetos mutáveis como objetos imutáveis"**
   - Parcialmente correto: usa versioning (cada versão é imutável), e o AGUID referencia o fluxo de versões. O certificado assinado e o anel interno com consenso Bizantino são o mecanismo para mutabilidade controlada.

7. **"Replicar dados em P2P garante disponibilidade"**
   - Incompleto: réplicas em nós da mesma organização, localização geográfica, jurisdição ou conectividade podem cair simultaneamente. GUIDs aleatórios distribuem réplicas aleatoriamente, reduzindo esse risco.

---

## Questões de Revisão

1. Explique as três gerações de sistemas P2P e por que o Napster, mesmo sendo da 1ª geração, foi historicamente importante. Quais foram suas limitações técnicas e legais?

2. Descreva os seis requisitos não funcionais que um middleware P2P deve satisfazer. Para cada um, explique como o Pastry o trata.

3. Compare as interfaces DHT e DOLR. Em que situações a aplicação preferiria controlar ela mesma o posicionamento de réplicas (DOLR) em vez de delegar ao middleware (DHT)?

4. Descreva os dois estágios do algoritmo de roteamento do Pastry. O que garante a correção do Estágio I? O que garante a eficiência do Estágio II?

5. Um nó com GUID `65A1FC` recebe uma mensagem para `D46A1C`. Sua tabela de roteamento tem uma entrada para `D46` na linha 0. Trace o caminho do roteamento explicando quais linhas da tabela e quais entradas do leaf set são consultados.

6. Explique o protocolo de integração de novos nós no Pastry. Por que a linha 0 da tabela de roteamento de X vem de A (vizinho de rede), mas a linha 1 vem de B (primeiro nó no caminho)?

7. Compare sistemas P2P estruturados e não estruturados em termos de garantias de localização, overhead de mensagens e resiliência. Por que os não estruturados dominam o compartilhamento de arquivos na prática?

8. Descreva o mecanismo QRP do Gnutella 0.6. Como a QRT de um ultrapar é construída e como ela é usada para evitar consultas desnecessárias?

9. O OceanStore usa três tipos de GUIDs (BGUID, VGUID, AGUID). Explique para que serve cada um e por que o AGUID não pode ser derivado do conteúdo do objeto.

10. O Ivy usa logs por participante e modos de visualização para segurança. Explique como um participante mal-intencionado é tratado e como os arquivos deletados por ele são recuperados.

---

## Referência

> COULOURIS, G. et al. **Sistemas Distribuídos: Conceitos e Projeto**. 5ª ed. Porto Alegre: Bookman, 2013. Capítulo 10, pp. 423–461.
