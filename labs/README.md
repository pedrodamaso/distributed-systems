# Message Brokers — Pub/Sub com RabbitMQ

Sistema de pedidos de e-commerce demonstrando o padrão **publish/subscribe** com RabbitMQ. Um produtor publica pedidos em um **fanout exchange** e três consumidores independentes reagem a cada evento simultaneamente.

```
[producer.py] ──► Exchange "pedidos" (fanout) ──► fila_estoque    ──► [consumer_estoque.py]
                                               ──► fila_email      ──► [consumer_email.py]
                                               ──► fila_faturamento──► [consumer_faturamento.py]
```

---

## Pré-requisitos

- Docker e Docker Compose
- Python 3.10+

---

## Início rápido

```bash
# 1. Subir o RabbitMQ
docker compose up -d

# 2. Instalar dependências Python
pip install -r requirements.txt

# 3. Abrir o painel de administração
# http://localhost:15672  →  usuário: admin  |  senha: admin123
```

Abra **4 terminais** e execute um serviço em cada:

```bash
# Terminal 1
python consumer_estoque.py

# Terminal 2
python consumer_email.py

# Terminal 3
python consumer_faturamento.py

# Terminal 4 — inicia o fluxo de pedidos
python producer.py
```

Ou use o Makefile:

```bash
make estoque      # terminal 1
make email        # terminal 2
make faturamento  # terminal 3
make producer     # terminal 4
```

---

## Estrutura

```
.
├── docker-compose.yml       # RabbitMQ com management plugin
├── requirements.txt         # pika==1.3.2
├── producer.py              # publica pedidos no exchange fanout
├── consumer_estoque.py      # baixa itens do inventário
├── consumer_email.py        # envia confirmação ao cliente
├── consumer_faturamento.py  # emite nota fiscal e acumula totais
├── consumer_dlq.py          # (Bônus) retry + Dead Letter Queue
├── Makefile                 # atalhos para todos os comandos
└── ATIVIDADE.md             # enunciado completo com experimentos
```

---

## Experimentos

### A — Consumidor lento (durabilidade de fila)

1. Pare o `consumer_email.py` com Ctrl+C
2. Deixe o `producer.py` rodar por ~30 segundos
3. Observe a `fila_email` acumular mensagens no painel
4. Reinicie o `consumer_email.py` — as mensagens são entregues

### B — Broker cai (persistência de mensagens)

```bash
make experimento-b-derrubar   # para o RabbitMQ
make experimento-b-restaurar  # reinicia e verifica que os dados persistiram
```

> Requer `durable=True` nas filas **e** `delivery_mode=2` nas mensagens.

### C — Múltiplas instâncias (load balancing vs. pub/sub)

Abra 3 terminais rodando `consumer_estoque.py` simultaneamente. Observe que cada mensagem é entregue a **apenas uma** instância — pois todas compartilham a mesma fila (`fila_estoque`). Compare com `consumer_email.py`, que usa `fila_email` separada e recebe **todas** as mensagens.

---

## Bônus — Dead Letter Queue

```bash
python consumer_dlq.py
```

Simula falhas aleatórias (40% de chance) com até 3 tentativas. Após esgotar as tentativas, a mensagem vai para `fila_morta` em vez de ser descartada.

Verifique a DLQ em: http://localhost:15672 → Queues → `fila_morta`

---

## Comandos úteis

```bash
make up          # sobe o RabbitMQ
make down        # para os containers
make logs        # acompanha logs do broker
make status      # verifica saúde do RabbitMQ
make clean       # remove containers e volumes (apaga dados)
make help        # lista todos os comandos disponíveis
```

---

## Referências

- [RabbitMQ Tutorials — Python](https://www.rabbitmq.com/tutorials/tutorial-three-python)
- [pika Documentation](https://pika.readthedocs.io/)
- TANENBAUM, A.; VAN STEEN, M. *Distributed Systems*, Cap. 4
