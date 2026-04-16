# Lab 02 — Message Brokers: Pub/Sub com RabbitMQ

## Metadados
- **Nível**: Intermediário
- **Tempo estimado**: 2–3 horas
- **Pré-requisitos**: Python básico, Docker/Docker Compose, conceito de filas
- **Conceitos abordados**: Pub/Sub, fanout exchange, durabilidade de mensagens, at-least-once delivery, acknowledgment, dead letter queue
- **Ferramentas**: Python 3.10+, RabbitMQ 3.13, Docker Compose, pika

---

## Contexto e Motivação

A **ShopFast** é uma startup de e-commerce que processa milhares de pedidos por hora. Quando um cliente finaliza uma compra, três coisas precisam acontecer **simultaneamente**:

1. **Serviço de Estoque** — baixar os itens do inventário
2. **Serviço de Email** — enviar confirmação ao cliente
3. **Serviço de Faturamento** — emitir a nota fiscal

No sistema legado, o servidor de pedidos chamava cada serviço de forma síncrona (HTTP sequencial). Resultado: se o serviço de email ficasse lento, **todo o fluxo travava**. Se ele caísse, o pedido era perdido.

A solução é usar um **Message Broker com padrão Pub/Sub**: o servidor de pedidos publica um evento e todos os serviços reagem de forma independente e assíncrona.

```
                    ┌──────────────────────────────┐
                    │        RabbitMQ              │
                    │                              │
                    │   ┌─── Exchange (fanout) ──┐ │
[Produtor]  ──────► │   │                        │ │
 (pedidos)          │   └──┬──────────┬─────────┘ │
                    │      │          │      │     │
                    │  fila_estoque  fila_email fila_faturamento
                    └──────┼──────────┼──────┼────┘
                           │          │      │
                    [Estoque]    [Email]  [Faturamento]
```

---

## Objetivos de Aprendizado

Ao final, o aluno será capaz de:
- Explicar a diferença entre filas ponto-a-ponto e o padrão pub/sub
- Configurar um **fanout exchange** no RabbitMQ e vincular múltiplas filas
- Implementar produtores e consumidores em Python com `pika`
- Usar **acknowledgment** para garantir at-least-once delivery
- Observar o comportamento do sistema sob falha de consumidor
- Explicar o trade-off entre durabilidade e performance

---

## Estrutura de Arquivos

```
message-brokers-rabbitmq/
├── ATIVIDADE.md          ← você está aqui
├── docker-compose.yml    ← sobe o RabbitMQ
├── requirements.txt
├── producer.py           ← gerador de pedidos
├── consumer_estoque.py   ← serviço de estoque
├── consumer_email.py     ← serviço de notificação
├── consumer_faturamento.py ← serviço de faturamento
├── consumer_dlq.py       ← (Bônus) Dead Letter Queue
└── Makefile
```

---

## Parte 1 — Subindo a Infraestrutura

### 1.1 Iniciar o RabbitMQ

```bash
# Na raiz do lab
docker compose up -d

# Verifique que o container está saudável
docker compose ps
```

Após ~10 segundos, acesse o **painel de administração**:
- URL: http://localhost:15672
- Usuário: `admin` / Senha: `admin123`

> **Explore**: Em *Exchanges*, você verá os exchanges padrão do RabbitMQ. Após rodar o produtor, um exchange `pedidos` do tipo `fanout` aparecerá.

### 1.2 Instalar dependências Python

```bash
pip install -r requirements.txt
```

---

## Parte 2 — Entendendo o Código

### 2.1 O Exchange Fanout

No RabbitMQ, o **exchange** é o componente que recebe mensagens e as distribui para filas. O tipo **fanout** entrega uma cópia para **todas** as filas vinculadas — independente de qualquer filtro.

```python
channel.exchange_declare(
    exchange="pedidos",
    exchange_type="fanout",   # cópia para TODAS as filas bound
    durable=True              # sobrevive a restart do broker
)
```

Cada consumidor cria **sua própria fila** e a vincula ao exchange:

```python
channel.queue_declare(queue="fila_estoque", durable=True)
channel.queue_bind(exchange="pedidos", queue="fila_estoque")
```

### 2.2 Durabilidade

| Componente   | Parâmetro            | Efeito                                 |
|-------------|----------------------|----------------------------------------|
| Exchange     | `durable=True`       | Sobrevive a restart do broker          |
| Fila         | `durable=True`       | Sobrevive a restart do broker          |
| Mensagem     | `delivery_mode=2`    | Persiste em disco (não apenas memória) |

### 2.3 Acknowledgment

O consumidor só confirma o processamento **após** concluir com sucesso:

```python
def processar_pedido(channel, method, properties, body):
    pedido = json.loads(body)
    # ... processa o pedido ...
    channel.basic_ack(delivery_tag=method.delivery_tag)  # confirma
```

Se o consumidor cair **antes** do `ack`, o RabbitMQ reentrega a mensagem a outro consumidor (at-least-once delivery).

---

## Parte 3 — Executando o Sistema

Abra **4 terminais separados**:

**Terminal 1 — Serviço de Estoque:**
```bash
python consumer_estoque.py
```

**Terminal 2 — Serviço de Email:**
```bash
python consumer_email.py
```

**Terminal 3 — Serviço de Faturamento:**
```bash
python consumer_faturamento.py
```

**Terminal 4 — Produtor de Pedidos:**
```bash
python producer.py
```

Observe no painel em http://localhost:15672 → *Queues* como as mensagens fluem para cada fila.

---

## Parte 4 — Experimentos de Falha

### Experimento A: Consumidor lento

1. Pare o `consumer_email.py` (Ctrl+C)
2. Deixe o produtor rodar por 30 segundos
3. Observe no painel: a `fila_email` acumula mensagens
4. Reinicie o `consumer_email.py`

**Pergunta:** O que acontece com as mensagens acumuladas? Elas se perdem?

### Experimento B: Broker cai com mensagens na fila

1. Com produtor e consumidores rodando, pare o RabbitMQ:
   ```bash
   docker compose stop rabbitmq
   ```
2. Reinicie:
   ```bash
   docker compose start rabbitmq
   ```

**Pergunta:** As mensagens que estavam nas filas persistiram? Por quê?

### Experimento C: Múltiplas instâncias do mesmo consumidor

1. Abra 3 terminais rodando `consumer_estoque.py` simultaneamente
2. Observe a distribuição de mensagens entre as instâncias

**Pergunta:** Como o RabbitMQ distribui as mensagens? Isso é pub/sub ou load balancing?

> **Dica:** Todos os 3 consumidores de estoque estão na mesma fila `fila_estoque`. Compare com o comportamento de `consumer_email.py` rodando em paralelo — ele usa `fila_email`, separada.

---

## (Bônus) Parte 5 — Dead Letter Queue

Quando uma mensagem é rejeitada (`basic_nack`) após muitas tentativas, para onde ela vai?

```bash
python consumer_dlq.py
```

Este consumidor simula falhas aleatórias e redireciona mensagens problemáticas para uma **Dead Letter Queue (DLQ)**, onde podem ser inspecionadas sem travar o fluxo normal.

---

## Critérios de Avaliação

| Critério | Peso | Descrição |
|---|---|---|
| Sistema funcional | 30% | Produtor e 3 consumidores rodando e processando mensagens |
| Experimentos documentados | 30% | Resultados dos experimentos A, B e C com capturas/logs |
| Perguntas de reflexão | 25% | Respostas fundamentadas nos conceitos teóricos |
| Bônus: DLQ implementada | 15% | consumer_dlq.py funcional com lógica de retry e DLQ |

---

## Perguntas de Reflexão

1. **Pub/Sub vs Ponto-a-ponto**: No Experimento C, quando rodou 3 instâncias de `consumer_estoque.py`, cada mensagem foi entregue a UMA instância, não às três. Isso é pub/sub ou filas tradicionais? Como você configuraria para que **todas** as 3 instâncias recebessem **todas** as mensagens?

2. **At-least-once vs Exactly-once**: Se o consumidor processar um pedido com sucesso mas cair **antes** de enviar o `ack`, a mensagem será reentregue. Isso pode gerar nota fiscal duplicada. Como você mitigaria esse problema na prática?

3. **Teorema CAP**: O RabbitMQ com `durable=True` prioriza Consistência ou Disponibilidade durante uma partição de rede? Justifique.

4. **Backpressure**: Se o `consumer_email.py` for 10× mais lento que o produtor, o que acontece com o sistema ao longo do tempo? Quais estratégias o RabbitMQ oferece para lidar com isso?

5. **Comparação com HTTP síncrono**: Liste 3 vantagens e 2 desvantagens do uso de message broker em comparação com chamadas HTTP diretas entre os serviços.

---

## Dicas e Armadilhas Comuns

- **`durable=True` na fila NÃO basta** — a mensagem também precisa de `delivery_mode=2` para ser persistida em disco.
- **`basic_qos(prefetch_count=1)`** impede que um consumidor receba mais mensagens do que consegue processar, evitando filas desequilibradas.
- **Evite** declarar o exchange com tipos diferentes em consumers e producers — causará erro de `PRECONDITION_FAILED`.
- O painel de administração (porta 15672) é seu melhor amigo para debugar: veja filas, mensagens acumuladas e taxa de consumo em tempo real.
- Se receber `ConnectionRefusedError`, aguarde o RabbitMQ ficar saudável: `docker compose ps` mostrará o status.

---

## Referências

- [RabbitMQ Tutorials — Python](https://www.rabbitmq.com/tutorials/tutorial-three-python)
- [pika Documentation](https://pika.readthedocs.io/)
- TANENBAUM, A.; VAN STEEN, M. *Distributed Systems*, Cap. 4 — Communication
- [CloudAMQP: RabbitMQ Best Practices](https://www.cloudamqp.com/blog/part1-rabbitmq-best-practice.html)
- [Understanding AMQP — exchanges, queues, bindings](https://www.rabbitmq.com/tutorials/amqp-concepts)
