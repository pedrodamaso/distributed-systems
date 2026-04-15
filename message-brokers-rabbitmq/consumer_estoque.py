"""
Consumidor — Serviço de Estoque
================================
Recebe cada pedido e atualiza o inventário de produtos.

Fila: fila_estoque (vinculada ao exchange 'pedidos')
Prefetch: 1 (processa uma mensagem por vez)
Ack: manual (após processamento bem-sucedido)

EXPERIMENTO C: rode múltiplas instâncias deste arquivo.
Observe que as mensagens são DISTRIBUÍDAS entre as instâncias
(load balancing), não duplicadas — pois todas compartilham a mesma fila.
"""

import pika
import json
import time
import random
import os

RABBITMQ_URL = "amqp://admin:admin123@localhost:5672/"
EXCHANGE_NAME = "pedidos"
QUEUE_NAME = "fila_estoque"

# Simula inventário local (em produção seria um banco de dados)
ESTOQUE = {
    "P001": 50, "P002": 200, "P003": 100,
    "P004": 30, "P005": 80,  "P006": 150, "P007": 120,
}

INSTANCIA = os.getpid()  # ID do processo para distinguir instâncias paralelas
processados = 0


def processar_pedido(channel, method, properties, body):
    global processados

    pedido = json.loads(body)
    produto_id = pedido["produto"]["id"]
    quantidade = pedido["quantidade"]
    nome_produto = pedido["produto"]["nome"]

    print(f"  [Estoque:{INSTANCIA}] Recebido pedido {pedido['pedido_id']} — {nome_produto} x{quantidade}")

    # Simula latência de consulta ao banco de dados
    time.sleep(random.uniform(0.3, 0.8))

    estoque_atual = ESTOQUE.get(produto_id, 0)

    if estoque_atual >= quantidade:
        ESTOQUE[produto_id] = estoque_atual - quantidade
        processados += 1
        print(
            f"  [Estoque:{INSTANCIA}] ✓ Baixado {quantidade}x '{nome_produto}' | "
            f"Saldo: {ESTOQUE[produto_id]} unidades restantes"
        )
    else:
        print(
            f"  [Estoque:{INSTANCIA}] ✗ SEM ESTOQUE para '{nome_produto}' | "
            f"Disponível: {estoque_atual} | Solicitado: {quantidade}"
        )

    # Confirma que a mensagem foi processada.
    # Se o consumidor cair antes deste ponto, o RabbitMQ reentrega a mensagem.
    channel.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()

    # Declara exchange (idempotente — ok se já existir)
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="fanout", durable=True)

    # Declara fila durável e vincula ao exchange
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME)

    # prefetch_count=1: só recebe próxima mensagem após confirmar a atual
    # Evita que um consumidor lento acumule mensagens não processadas
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=processar_pedido)

    print(f"[Estoque:{INSTANCIA}] Aguardando pedidos na fila '{QUEUE_NAME}'...")
    print(f"[Estoque:{INSTANCIA}] Estoque inicial: {ESTOQUE}")
    print(f"[Estoque:{INSTANCIA}] Pressione Ctrl+C para encerrar.\n")

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print(f"\n[Estoque:{INSTANCIA}] Encerrado. Pedidos processados: {processados}")
        channel.stop_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
