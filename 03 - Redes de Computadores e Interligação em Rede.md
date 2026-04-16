# Sistemas Distribuídos — Capítulo 3: Redes de Computadores e Interligação em Rede
**Livro:** Coulouris et al. — *Sistemas Distribuídos: Conceitos e Projeto*
**Disciplina:** Sistemas Distribuídos | Graduação em Sistemas de Informação

---

## Objetivo de Aprendizagem

Ao final do estudo deste capítulo, o aluno deve ser capaz de:

- Identificar os tipos de rede e seus parâmetros de desempenho (latência, largura de banda)
- Explicar os conceitos de comutação de pacotes, protocolos em camadas e encapsulamento
- Descrever o funcionamento do esquema de endereçamento IPv4 e os mecanismos NAT e CIDR
- Compreender os protocolos TCP e UDP e suas diferenças
- Explicar o funcionamento básico do roteamento e do controle de congestionamento
- Entender o papel de firewalls e VPNs na segurança de redes em sistemas distribuídos
- Reconhecer as características das tecnologias Ethernet, WiFi e Bluetooth

---

## Pré-requisitos

- Capítulo 1: conceito de sistema distribuído, Internet, intranets, firewalls
- Capítulo 2: modelos fundamentais — latência, largura de banda, jitter; modelos físicos de SD

---

## Por que redes importam para Sistemas Distribuídos?

O desempenho, a confiabilidade, a escalabilidade, a mobilidade e a qualidade de serviço das redes subjacentes **afetam diretamente o comportamento dos sistemas distribuídos**. Projetar um SD sem entender as propriedades das redes sobre as quais ele opera é como projetar um prédio sem entender as propriedades do solo.

**Dado importante:** o tempo para uma requisição em rede local é ~0,5 ms vs. ~1 µs para acesso a objeto na memória local — diferença de **1000×**. Na Internet, a latência é de 5 a 500 ms — **10 a 100× pior** que a rede local. Isso impõe restrições fundamentais ao design de sistemas distribuídos.

---

## 1. Requisitos de Rede para Sistemas Distribuídos

| Requisito | Descrição | Relevância para SD |
|---|---|---|
| **Desempenho** | Latência e taxa de transferência ponto a ponto | Determina o tempo de resposta de operações remotas |
| **Escalabilidade** | Suporte ao crescimento de bilhões de nós | Mecanismos de endereçamento e roteamento devem evoluir |
| **Confiabilidade** | Frequência e tipo de falhas esperadas | SD deve tolerar perdas de pacotes, duplicatas, reordenação |
| **Segurança** | Proteção contra acesso não autorizado | Firewalls, VPN, criptografia fim a fim |
| **Mobilidade** | Dispositivos que mudam de ponto de conexão | Mecanismos de mobilidade IP para conectividade contínua |
| **Qualidade de Serviço (QoS)** | Garantias de latência e largura de banda para mídia em tempo real | Necessário para áudio/vídeo distribuído |
| **Multicast** | Envio de uma mensagem para múltiplos destinatários simultaneamente | Eficiente para atualizações de grupo, streaming |

**Fórmula do tempo de transmissão:**
```
Tempo de transmissão = latência + (tamanho da mensagem / taxa de transferência)
```

> Nas redes locais, a latência domina para mensagens pequenas — o que é o caso típico em sistemas distribuídos (muitas mensagens curtas de coordenação).

---

## 2. Tipos de Rede

| Tipo | Acrônimo | Alcance | Largura de Banda | Latência | Exemplos |
|---|---|---|---|---|---|
| Rede Pessoal | PAN/WPAN | 10–30 m | 0,5–2 Mbps | 5–20 ms | Bluetooth |
| Rede Local | LAN | 1–2 km | 10–10.000 Mbps | 1–10 ms | Ethernet |
| Rede Metropolitana | MAN | 2–50 km | 1–600 Mbps | 10 ms | ATM, DSL, cabo |
| Rede de Longa Distância | WAN | Mundial | 0,01–600 Mbps | 100–500 ms | Roteamento IP |
| WLAN | WiFi | 0,15–1,5 km | 11–108 Mbps | 5–20 ms | IEEE 802.11 |
| WMAN | WiMAX | 5–50 km | 1,5–20 Mbps | 5–20 ms | IEEE 802.16 |
| WWAN | Celular | Nacional/global | 348 Kbps–14,4 Mbps | 100–500 ms | 3G/4G (UMTS) |

**Inter-redes:** rede composta por múltiplas redes heterogêneas integradas sob um protocolo comum (ex: IP). A Internet é o maior exemplo — abstrai a diversidade de tecnologias subjacentes em um único serviço de comunicação.

**Erros comuns em redes:**
- Perda de pacotes: descarte em buffers cheios em nós intermediários
- Reordenação: pacotes de uma mesma mensagem podem chegar fora de ordem (em WANs)
- Duplicatas: retransmissões indevidas geram cópias do mesmo pacote

---

## 3. Conceitos Básicos de Redes

### 3.1 Comutação de Pacotes

Técnica fundamental das redes de computadores: mensagens são subdivididas em **pacotes** de comprimento limitado, transmitidos independentemente.

**Por que usar pacotes?**
- Permite alocar buffer máximo fixo em cada nó
- Evita bloqueio do canal por mensagens longas
- Permite que múltiplas comunicações compartilhem o mesmo enlace

### 3.2 Fluxo de Dados (Streaming)

Transmissão contínua de áudio e vídeo em tempo real. Características:
- Requer largura de banda alta e garantida (~1,5 Mbps para vídeo comprimido; ~120 Mbps sem compressão)
- Cada elemento tem um **tempo de reprodução** (playback time) — elementos que chegam após esse prazo são descartados
- Usa protocolo UDP (não orientado à conexão) para menor overhead
- **RTP** (Real-Time Transport Protocol): protocolo de aplicação que inclui timestamp e número de sequência para sincronização
- **RSVP** (Resource Reservation Protocol): permite reserva prévia de largura de banda para fluxos em tempo real

> **Implicação para QoS:** a Internet padrão não oferece garantias de latência ou largura de banda. Para streaming confiável, são necessárias reservas de recursos (QoS) ou uso de intranets controladas.

### 3.3 Esquemas de Comutação

| Esquema | Como funciona | Vantagem | Desvantagem |
|---|---|---|---|
| **Broadcast** | Transmite para todos; receptor filtra | Simples, sem configuração | Tráfego desnecessário em todos os nós |
| **Comutação de circuitos** | Estabelece circuito físico dedicado antes de transmitir | Latência constante, QoS garantido | Recursos reservados mesmo sem uso (POTS/telefonia) |
| **Comutação de pacotes** | Pacotes roteados independentemente, armazenados e encaminhados (store-and-forward) | Eficiente no uso de recursos, resiliente a falhas | Latência variável |
| **Frame relay / ATM** | Pequenos pacotes (frames/células) comutados por número de circuito virtual | Baixa latência, suporta QoS | Fase de configuração inicial |

**Datagramas vs. Circuitos Virtuais:**
- **Datagramas:** cada pacote carrega endereços de origem e destino; pacotes de uma mesma mensagem podem seguir rotas diferentes → base do IP
- **Circuitos virtuais:** rota estabelecida antes; pacotes identificados por número de circuito (sem endereços completos) → base do ATM

### 3.4 Protocolos e Camadas

> **Protocolo** é um conjunto bem definido de regras e formatos para comunicação entre processos: especifica a sequência de mensagens a trocar e o formato dos dados.

**Organização em camadas (pilha de protocolos):** cada camada oferece serviços à camada acima usando os serviços da camada abaixo.

**Modelo OSI (7 camadas):**

| Camada | Função | Exemplos |
|---|---|---|
| 7 - Aplicação | Protocolos de aplicações específicas | HTTP, FTP, SMTP, CORBA IIOP |
| 6 - Apresentação | Representação de dados independente de plataforma; criptografia | TLS, CORBA Data Rep. |
| 5 - Sessão | Confiabilidade, detecção e recuperação de falhas | SIP |
| 4 - Transporte | Mensagens fim-a-fim, endereçamento por portas | TCP, UDP |
| 3 - Rede | Transferência de pacotes entre hosts; roteamento | IP, ATM |
| 2 - Enlace | Transmissão entre nós diretamente conectados | Ethernet MAC, PPP |
| 1 - Física | Transmissão de bits; sinalização elétrica/óptica/rádio | Ethernet, ISDN |

**Encapsulamento:** ao descer pelas camadas no remetente, cada camada adiciona um cabeçalho com informações de controle. No destino, as camadas removem os cabeçalhos correspondentes (desencapsulamento).

```
Dados da Aplicação
+ Cabeçalho de Transporte (TCP/UDP)
+ Cabeçalho de Rede (IP)
+ Cabeçalho de Enlace (Ethernet)
= Quadro transmitido no fio
```

**MTU (Maximum Transfer Unit):** tamanho máximo de pacote da rede subjacente (Ethernet: 1.500 bytes). Mensagens maiores são **fragmentadas** (segmentadas) antes da transmissão e remontadas no destino.

**Custo das camadas:** N camadas = N transferências de controle + N cópias de dados → overhead significativo no desempenho.

---

## 4. Protocolos Internet (TCP/IP)

### 4.1 Visão Geral da Pilha TCP/IP

A pilha TCP/IP tem **4 camadas** (simplificando o OSI):

```
┌────────────────────────────────┐
│        Aplicação               │  HTTP, FTP, SMTP, DNS...
├────────────────────────────────┤
│        Transporte              │  TCP / UDP
├────────────────────────────────┤
│        Rede (Inter-rede)       │  IP (IPv4/IPv6)
├────────────────────────────────┤
│  Interface de Rede / Enlace    │  Ethernet, WiFi, PPP...
└────────────────────────────────┘
```

O **IP** é a "cola" da Internet: fornece endereçamento universal e transmissão de datagramas entre qualquer par de hosts, independentemente das tecnologias de rede subjacentes.

### 4.2 Endereçamento IPv4

- Endereço de **32 bits** (4 octetos) → ~4 bilhões de endereços
- Estrutura: **ID de rede + ID de host** no mesmo endereço

| Classe | 1º octeto | Hosts por rede | Uso |
|---|---|---|---|
| A | 1–127 | ~16 milhões | Grandes redes nacionais |
| B | 128–191 | ~65.000 | Organizações médias |
| C | 192–223 | 254 | Redes pequenas |
| D | 224–239 | — | Multicast |

**Problema:** esgotamento dos endereços IP previsto desde os anos 90. Três soluções:

1. **IPv6** (endereços de 128 bits)
2. **CIDR** (Classless InterDomain Routing): eliminação das classes fixas; máscaras de tamanho variável permitem alocação mais eficiente
3. **NAT** (Network Address Translation): múltiplos hosts internos compartilham um único IP público

#### NAT — Network Address Translation

```
[192.168.1.10] ──┐
[192.168.1.11] ──┼──► [Roteador NAT: 83.215.152.95] ──► Internet
[192.168.1.12] ──┘
```

**Funcionamento:**
- Hosts internos usam endereços privados (ex: 192.168.1.x)
- Roteador NAT mantém tabela de mapeamento (IP interno + porta) ↔ porta virtual externa
- Substitui endereço de origem nas mensagens saintes; faz o processo inverso nas respostas

**Limitação:** hosts com NAT não podem facilmente atuar como servidores (requisições externas não chegam diretamente).

### 4.3 IPv6

- Endereços de **128 bits** → 340 undecilhões de endereços
- Cabeçalho simplificado e fixo (melhor desempenho nos roteadores)
- Suporte nativo a QoS (rótulo de fluxo), segurança (IPSec) e mobilidade
- **Tunelamento:** durante a transição, pacotes IPv6 são encapsulados em datagramas IPv4 para atravessar redes ainda IPv4

### 4.4 Protocolo IP: Características Essenciais

- **Serviço de melhor esforço (best-effort):** sem garantia de entrega; pacotes podem ser perdidos, duplicados, reordenados ou atrasados
- **Checksum apenas no cabeçalho** (não nos dados) → eficiência nos roteadores; protocolos superiores (TCP/UDP) garantem integridade dos dados
- **Fragmentação:** datagramas maiores que o MTU da rede subjacente são fragmentados e remontados no destino
- **IP Spoofing:** endereço de origem pode ser falsificado → base de muitos ataques DoS

### 4.5 Resolução de Endereços — ARP

**ARP** (Address Resolution Protocol) converte endereço IP (lógico) em endereço MAC Ethernet (físico).

**Funcionamento:**
1. Host A precisa enviar para IP 192.168.1.10 na mesma rede local
2. Envia broadcast ARP: "Quem tem o IP 192.168.1.10?"
3. Host 192.168.1.10 responde com seu endereço MAC
4. Host A armazena o par IP↔MAC em sua cache ARP

### 4.6 Roteamento IP

**Algoritmo de Vetor de Distância (RIP):**
- Cada nó mantém tabela de roteamento com custo (número de hops) para cada destino
- Periodicamente, troca sua tabela com vizinhos imediatos
- Atualiza rotas quando encontra caminho mais curto ou quando vizinho é autoridade sobre uma rota
- Problema: convergência lenta após falhas

**Algoritmo de Estado de Enlace (OSPF):**
- Cada nó mantém banco de dados de toda a topologia conhecida
- Usa algoritmo de Dijkstra (menor caminho)
- Convergência mais rápida que RIP
- Protocolo dominante nos roteadores modernos

**Rotas padrão (default routes):** roteadores não precisam conhecer todas as rotas do mundo. Um roteador de borda direciona para um gateway superior tudo o que não está em sua tabela local.

**CIDR e máscaras de sub-rede:** permitem agregar múltiplas redes de classe C em uma única entrada da tabela de roteamento, reduzindo enormemente o tamanho das tabelas nos roteadores de backbone.

### 4.7 Controle de Congestionamento

Quando a carga ultrapassa ~80% da capacidade de um enlace:
- Filas crescem até esgotar buffers
- Pacotes são descartados
- Retransmissões agravam o problema

**Mecanismos:**
- **Pacotes reguladores (choke packets):** nós congestionados enviam sinal pedindo redução na taxa de envio
- **Controle fim a fim (TCP):** remetente reduz taxa baseado em ACKs e perdas
- **Observação de perdas:** ausência de ACK indica congestionamento

### 4.8 Interligação de Redes — Dispositivos

| Dispositivo | Camada de operação | Função |
|---|---|---|
| **Hub** | Física (1) | Conecta segmentos Ethernet; retransmite tudo para todas as portas (broadcast) |
| **Switch** | Enlace (2) | Interliga redes Ethernet; direciona quadros apenas para a porta correta |
| **Roteador** | Rede (3) | Encaminha pacotes IP entre diferentes redes; mantém tabela de roteamento |
| **Bridge** | Enlace (2) | Liga redes de tipos diferentes |
| **Gateway** | Aplicação (7) | Traduz entre protocolos ou aplicações incompatíveis |

**Tunelamento:** técnica para encapsular pacotes de um protocolo dentro de outro, permitindo tráfego em redes incompatíveis (ex: IPv6 sobre IPv4, VPN sobre Internet pública).

### 4.9 Protocolos de Transporte: TCP e UDP

| Característica | TCP | UDP |
|---|---|---|
| **Orientação à conexão** | Sim (estabelecimento com handshake 3 vias) | Não |
| **Entrega confiável** | Sim (confirmações, retransmissões) | Não |
| **Ordem dos dados** | Garantida | Não garantida |
| **Controle de fluxo** | Sim | Não |
| **Controle de congestionamento** | Sim | Não |
| **Overhead** | Alto | Baixo |
| **Uso típico** | HTTP, FTP, SMTP, SSH | DNS, streaming de vídeo/voz, jogos online |

**Portas bem conhecidas:**
- HTTP: 80 | HTTPS: 443 | FTP: 21 | SSH: 22 | SMTP: 25 | DNS: 53

**Portas < 1023:** reservadas para processos privilegiados do SO
**Portas 1024–49151:** registradas na IANA
**Portas 49152–65535:** uso dinâmico/privado

### 4.10 DNS — Domain Name System

Converte nomes de domínio (ex: `www.amazon.com`) em endereços IP.

- Hierarquia distribuída de servidores de nomes
- Cada nível da hierarquia gerencia uma parte do espaço de nomes
- Cache local nos resolvers para reduzir latência e carga
- Cada entrada tem um TTL (Time to Live) que controla a validade do cache

### 4.11 Firewalls e VPN

**Firewall:** posicionado no gateway da intranet, filtra mensagens de entrada e saída conforme a política de segurança da organização. Pode bloquear por IP, porta, protocolo ou conteúdo.

**Problema:** firewalls restringem aplicativos distribuídos legítimos que precisam de comunicação bidirecional.

**VPN (Virtual Private Network):** cria um túnel criptografado sobre a Internet pública, permitindo que hosts externos participem de uma intranet segura como se estivessem fisicamente presentes.

```
[Usuário remoto] ──► [Internet pública] ──► [Túnel VPN criptografado] ──► [Intranet corporativa]
```

---

## 5. Estudos de Caso: Ethernet, WiFi e Bluetooth

### 5.1 Ethernet (IEEE 802.3)

A tecnologia dominante para LANs cabeadas.

**Velocidades:** 10 Mbps → 100 Mbps → 1 Gbps → 10 Gbps

**Método de acesso ao meio:** CSMA/CD (Carrier Sense Multiple Access with Collision Detection)
- Dispositivo "escuta" o canal antes de transmitir
- Se detectar colisão, para e aguarda tempo aleatório antes de retransmitir
- Em redes comutadas (switches), colisões são eliminadas: cada porta tem seu próprio domínio de colisão

**Endereçamento MAC:** identificador único de 48 bits gravado na interface de rede pelo fabricante.

**MTU:** 1.500 bytes por quadro.

**Evolução:** redes Ethernet modernas são totalmente comutadas (switched Ethernet) — eliminam colisões, aumentam eficiência e permitem full-duplex.

### 5.2 WiFi (IEEE 802.11)

Principal tecnologia para WLANs sem fio.

**Método de acesso:** CSMA/CA (Collision Avoidance — evitação de colisões, pois detecção é impraticável no meio sem fio)

**Versões principais:**

| Padrão | Frequência | Velocidade máxima |
|---|---|---|
| 802.11b | 2,4 GHz | 11 Mbps |
| 802.11g | 2,4 GHz | 54 Mbps |
| 802.11n | 2,4/5 GHz | 600 Mbps |
| 802.11ac | 5 GHz | > 1 Gbps |

**Desafios específicos:**
- Interferência e obstáculos físicos afetam desempenho
- Handoff: quando dispositivo se move entre pontos de acesso
- Segurança: meio broadcast expõe tráfego → necessidade de WPA2/WPA3

**Infraestrutura:** pontos de acesso (Access Points) conectados à rede cabeada. Dispositivos se associam ao AP mais próximo.

### 5.3 Bluetooth (IEEE 802.15.1)

Tecnologia para WPANs — redes pessoais de curto alcance.

| Parâmetro | Valor |
|---|---|
| Alcance | 10–30 m |
| Velocidade | 0,5–2 Mbps |
| Frequência | 2,4 GHz |
| Latência | 5–20 ms |

**Organização:** **Piconet** = 1 mestre + até 7 escravos ativos.
**Frequency Hopping:** troca de canal 1.600 vezes/segundo para reduzir interferência.

**Casos de uso em SI:** conectividade de periféricos (teclados, mouses, fones), IoT, wearables, automação predial.

---

## 6. Síntese — Mapa Conceitual do Capítulo

```
REDES PARA SISTEMAS DISTRIBUÍDOS
│
├── Requisitos: desempenho | escalabilidade | confiabilidade | segurança | mobilidade | QoS | multicast
│
├── Tipos de rede:
│   ├── PAN/WPAN (Bluetooth) → 10 m
│   ├── LAN/WLAN (Ethernet/WiFi) → 1 km
│   ├── MAN (DSL/cabo) → 50 km
│   └── WAN/WWAN (IP/3G-4G) → global
│
├── Conceitos básicos:
│   ├── Comutação de pacotes (store-and-forward)
│   ├── Streaming (RTP, RSVP)
│   ├── Protocolos em camadas (OSI 7 camadas)
│   ├── Encapsulamento e MTU/fragmentação
│   ├── Datagramas vs. Circuitos Virtuais
│   ├── Roteamento: Vetor de Distância (RIP) e Estado de Enlace (OSPF)
│   └── Controle de Congestionamento
│
├── Protocolo Internet (TCP/IP):
│   ├── IPv4: 32 bits, classes A/B/C/D
│   ├── CIDR: máscaras variáveis, agregação de rotas
│   ├── NAT: endereços privados + IP público compartilhado
│   ├── IPv6: 128 bits + QoS + IPSec nativo
│   ├── ARP: IP → MAC
│   ├── TCP: confiável, orientado à conexão, controle de fluxo/congestionamento
│   ├── UDP: não confiável, sem conexão, baixo overhead
│   ├── DNS: nome → IP (hierarquia distribuída)
│   └── Firewall / VPN
│
└── Estudos de caso:
    ├── Ethernet: CSMA/CD, switched, 10 Mbps–10 Gbps
    ├── WiFi (802.11): CSMA/CA, 11–>1000 Mbps, handoff
    └── Bluetooth: piconet, frequency hopping, 10–30 m
```

---

## 7. Relação com Sistemas de Informação

| Conceito do Capítulo | Aplicação Prática em SI |
|---|---|
| **Latência vs. largura de banda** | Escolha de arquitetura: muitas chamadas RPCs curtas vs. poucas transferências em lote |
| **TCP vs. UDP** | APIs REST usam TCP; streaming de vídeo/voz e jogos usam UDP |
| **NAT e endereços privados** | Toda rede corporativa e doméstica usa NAT; afeta configuração de servidores |
| **DNS** | Resolução de nomes de serviços em microsserviços (service discovery) |
| **Firewall** | Controle de acesso a sistemas de informação corporativos |
| **VPN** | Acesso remoto seguro a sistemas ERP e bancos de dados corporativos |
| **WiFi** | Mobilidade de colaboradores em ambientes empresariais |
| **Bluetooth/IoT** | Coleta de dados em chão de fábrica, varejo, logística |
| **QoS** | Sistemas de videoconferência e call centers sobre IP (VoIP) |
| **Controle de congestionamento** | Dimensionamento de redes para sistemas de alto volume (e-commerce, bancos) |

---

## 8. Erros Comuns dos Alunos

| Equívoco | Correção |
|---|---|
| Confundir latência com tempo de transmissão total | Tempo total = latência + tamanho/taxa de transferência; latência é apenas o atraso inicial |
| Achar que TCP garante entrega em tempo real | TCP garante entrega correta e ordenada, mas sem garantia de tempo; UDP é preferido para tempo real |
| Confundir hub e switch | Hub faz broadcast para todas as portas; switch aprende os MACs e direciona para a porta correta |
| Achar que NAT resolve o esgotamento de IPv4 definitivamente | NAT é solução paliativa; IPv6 é a solução definitiva |
| Confundir fragmentação com segmentação TCP | Fragmentação: feita pela camada IP quando datagrama supera MTU; segmentação TCP: feita pela camada de transporte antes de passar ao IP |
| Achar que firewalls garantem segurança completa | Firewalls filtram com base em IP/porta/protocolo, mas não protegem contra ataques sofisticados (ex: injeção SQL sobre HTTP) nem contra ameaças internas |
| Confundir roteador e switch | Switch opera na camada de enlace (MAC); roteador opera na camada de rede (IP) |

---

## 9. Questões para Revisão e Discussão

1. Calcule o tempo de transmissão de uma mensagem de 1 MB em uma rede local Ethernet de 100 Mbps com latência de 5 ms. Compare com a transmissão pela Internet com latência de 100 ms e taxa de 10 Mbps.

2. Por que a latência tem importância igual ou maior que a taxa de transferência em sistemas distribuídos que trocam muitas mensagens curtas? Dê um exemplo prático.

3. Explique a diferença entre datagramas e circuitos virtuais. Quais as vantagens de cada abordagem para sistemas distribuídos?

4. Um aplicativo de videoconferência precisa de 2 Mbps garantidos e latência máxima de 50 ms. Qual protocolo de transporte (TCP ou UDP) é mais adequado e por quê? O que seria necessário para garantir a QoS exigida?

5. Descreva o processo completo de envio de uma requisição HTTP de um cliente (192.168.1.10) para um servidor Web (203.0.113.5), passando por um roteador NAT, considerando as camadas IP, TCP e HTTP.

6. Explique como o CIDR e o NAT adiaram o esgotamento dos endereços IPv4. Quais são as limitações de cada solução? Por que o IPv6 ainda é necessário?

7. Um sistema de gestão empresarial precisa ser acessado por funcionários remotos. Compare duas soluções: (a) exposição direta do servidor na Internet e (b) uso de VPN. Quais são os trade-offs de segurança e usabilidade?

8. Compare Ethernet, WiFi e Bluetooth considerando: largura de banda, latência, mobilidade, confiabilidade e casos de uso em um sistema de informação distribuído.

---

## Referência

COULOURIS, G. et al. **Sistemas Distribuídos: Conceitos e Projeto**. 5. ed. Porto Alegre: Bookman, 2013. Capítulo 3, p. 81–141.
