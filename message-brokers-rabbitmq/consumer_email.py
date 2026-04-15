"""
Consumidor — Serviço de Notificação por Email
===============================================
Recebe cada pedido e envia um email de confirmação ao cliente.

Fila: fila_email (vinculada ao exchange 'pedidos')
Latência simulada: 0.5–2s (mais lento que os outros serviços)

EXPERIMENTO A: pare este consumidor por 30s e observe a fila
acumular mensagens no painel. Ao reiniciá-lo, as mensagens
acumuladas serão processadas — graças à durabilidade da fila.
"""

import pika
import json
import time
import random

RABBITMQ_URL = "amqp://admin:admin123@localhost:5672/"
EXCHANGE_NAME = "pedidos"
QUEUE_NAME = "fila_email"

TEMPLATES_EMAIL = [
    "Olá, {cliente}! Seu pedido #{pedido_id} foi confirmado. "
    "Você receberá {nome_produto} em até 5 dias úteis.",

    "Confirmamos o recebimento do seu pedido #{pedido_id}, {cliente}! "
    "Total cobrado: R$ {total:.2f}. Obrigado pela preferência!",

    "Pedido #{pedido_id} em processamento! "
    "Produto: {nome_produto} x{quantidade}. "
    "Acompanhe o status em shopfast.com.br/pedidos.",
]

processados = 0


def simular_envio_email(pedido: dict) -> str:
    """Simula geração e envio de email ao cliente."""
    template = random.choice(TEMPLATES_EMAIL)
    return template.format(
        cliente=pedido["cliente"],
        pedido_id=pedido["pedido_id"],
        nome_produto=pedido["produto"]["nome"],
        quantidade=pedido["quantidade"],
        total=pedido["total"],
    )


def processar_pedido(channel, method, properties, body):
    global processados

    pedido = json.loads(body)
    email_destino = f"{pedido['cliente']}@shopfast.com"

    print(f"  [Email] Recebido pedido {pedido['pedido_id']} — preparando email para {email_destino}")

    # Serviço de email é mais lento (simulando integração com SMTP externo)
    time.sleep(random.uniform(0.5, 2.0))

    conteudo = simular_envio_email(pedido)
    processados += 1

    print(f"  [Email] ✉ Email #{processados:04d} enviado para {email_destino}")
    print(f"          Assunto: Confirmação do Pedido #{pedido['pedido_id']}")
    print(f"          Corpo: \"{conteudo[:80]}...\"")

    channel.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()

    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="fanout", durable=True)
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=processar_pedido)

    print(f"[Email] Aguardando pedidos na fila '{QUEUE_NAME}'...")
    print(f"[Email] Latência simulada: 0.5–2.0s por email")
    print(f"[Email] Pressione Ctrl+C para encerrar.\n")

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print(f"\n[Email] Encerrado. Emails enviados: {processados}")
        channel.stop_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
