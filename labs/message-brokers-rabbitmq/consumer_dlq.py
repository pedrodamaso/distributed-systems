"""
(BÔNUS) Consumidor com Retry e Dead Letter Queue (DLQ)
=======================================================
Demonstra o padrão de reprocessamento com limite de tentativas.

Quando uma mensagem falha mais de MAX_RETRIES vezes, ela é
redirecionada para a DLQ (Dead Letter Queue) em vez de ser
descartada — permitindo análise posterior.

Configuração:
  - Fila principal: fila_pedidos_dlq (com dead-letter-exchange)
  - DLQ: fila_morta (recebe mensagens rejeitadas)
  - Exchange DLQ: dlx_pedidos

Para observar a DLQ no painel:
  http://localhost:15672 → Queues → fila_morta

Conceitos:
  - x-dead-letter-exchange: redireciona msgs rejeitadas
  - x-message-ttl: expiração automática (para retry com delay)
  - basic_nack(requeue=False): rejeita sem recolocar na fila
"""

import pika
import json
import time
import random

RABBITMQ_URL = "amqp://admin:admin123@localhost:5672/"
EXCHANGE_NAME = "pedidos"
QUEUE_NAME = "fila_pedidos_dlq"
DLX_NAME = "dlx_pedidos"       # Dead Letter Exchange
DLQ_NAME = "fila_morta"        # Dead Letter Queue

MAX_RETRIES = 3                 # máximo de tentativas antes de ir para DLQ

processados = 0
rejeitados = 0


def configurar_filas(channel):
    """
    Configura o exchange principal, o DLX e as filas com DLQ.
    A fila principal aponta para o DLX quando uma mensagem é rejeitada.
    """
    # Exchange principal (compartilhado com os outros consumers)
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="fanout", durable=True)

    # Exchange DLQ: recebe mensagens mortas
    channel.exchange_declare(exchange=DLX_NAME, exchange_type="direct", durable=True)

    # Fila principal: ao rejeitar com requeue=False, mensagem vai para o DLX
    channel.queue_declare(
        queue=QUEUE_NAME,
        durable=True,
        arguments={
            "x-dead-letter-exchange": DLX_NAME,
            "x-dead-letter-routing-key": "morta",
        },
    )
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME)

    # Fila morta: recebe as mensagens que falharam demais
    channel.queue_declare(queue=DLQ_NAME, durable=True)
    channel.queue_bind(exchange=DLX_NAME, queue=DLQ_NAME, routing_key="morta")


def contar_tentativas(properties) -> int:
    """Extrai o número de tentativas anteriores dos headers da mensagem."""
    if properties.headers and "x-retry-count" in properties.headers:
        return properties.headers["x-retry-count"]
    return 0


def processar_pedido(channel, method, properties, body):
    global processados, rejeitados

    pedido = json.loads(body)
    tentativa = contar_tentativas(properties) + 1
    falha_simulada = random.random() < 0.4  # 40% de chance de falhar

    print(
        f"  [DLQ Consumer] Tentativa {tentativa}/{MAX_RETRIES} | "
        f"Pedido {pedido['pedido_id']} | "
        f"{'FALHA SIMULADA' if falha_simulada else 'processando...'}"
    )

    time.sleep(random.uniform(0.2, 0.5))

    if falha_simulada and tentativa < MAX_RETRIES:
        # Rejeita e republica manualmente com contador incrementado
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        # Republica com header atualizado (simula retry com backoff)
        novos_headers = {"x-retry-count": tentativa}
        time.sleep(tentativa * 0.5)  # backoff simples

        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key="",
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json",
                headers=novos_headers,
            ),
        )
        print(f"  [DLQ Consumer] ↻ Reenfileirado para tentativa {tentativa + 1}")

    elif falha_simulada and tentativa >= MAX_RETRIES:
        # Esgotou tentativas: manda para a DLQ
        rejeitados += 1
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        print(
            f"  [DLQ Consumer] ✗ Pedido {pedido['pedido_id']} enviado para DLQ "
            f"após {tentativa} tentativas."
        )

    else:
        # Sucesso
        processados += 1
        print(
            f"  [DLQ Consumer] ✓ Pedido {pedido['pedido_id']} processado com sucesso "
            f"(tentativa {tentativa}) | OK: {processados} | DLQ: {rejeitados}"
        )
        channel.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()

    configurar_filas(channel)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=processar_pedido)

    print(f"[DLQ Consumer] Aguardando pedidos na fila '{QUEUE_NAME}'...")
    print(f"[DLQ Consumer] Max retries: {MAX_RETRIES} | Taxa de falha simulada: 40%")
    print(f"[DLQ Consumer] Mensagens com falha vão para '{DLQ_NAME}'")
    print(f"[DLQ Consumer] Verifique a DLQ em http://localhost:15672 → Queues → {DLQ_NAME}")
    print(f"[DLQ Consumer] Pressione Ctrl+C para encerrar.\n")

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print(f"\n[DLQ Consumer] Encerrado.")
        print(f"[DLQ Consumer] Processados: {processados} | Enviados para DLQ: {rejeitados}")
        channel.stop_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
