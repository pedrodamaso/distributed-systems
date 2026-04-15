"""
Consumidor — Serviço de Faturamento
=====================================
Recebe cada pedido, emite nota fiscal e acumula totais.

Fila: fila_faturamento (vinculada ao exchange 'pedidos')
Destaque: mantém estado local (total acumulado) entre mensagens.

Ponto de reflexão: se este consumidor processar um pedido e cair
ANTES do basic_ack, a mensagem é reentregue — gerando NF duplicada.
Como evitar isso? (Veja pergunta de reflexão #2 na ATIVIDADE.md)
"""

import pika
import json
import time
import random
from datetime import datetime

RABBITMQ_URL = "amqp://admin:admin123@localhost:5672/"
EXCHANGE_NAME = "pedidos"
QUEUE_NAME = "fila_faturamento"

# Estado acumulado do serviço (em memória — perdido se o processo reiniciar)
total_faturado = 0.0
nfs_emitidas = 0


def emitir_nota_fiscal(pedido: dict, numero_nf: int) -> str:
    """Simula emissão de nota fiscal e retorna o número da NF."""
    mes_ano = datetime.now().strftime("%Y%m")
    return f"NF-{mes_ano}-{numero_nf:06d}"


def processar_pedido(channel, method, properties, body):
    global total_faturado, nfs_emitidas

    pedido = json.loads(body)

    print(f"  [Faturamento] Recebido pedido {pedido['pedido_id']} — gerando nota fiscal...")

    # Simula processamento fiscal (validação CNPJ, cálculo de impostos, etc.)
    time.sleep(random.uniform(0.2, 0.6))

    nfs_emitidas += 1
    total_faturado += pedido["total"]
    numero_nf = emitir_nota_fiscal(pedido, nfs_emitidas)

    print(
        f"  [Faturamento] ✓ {numero_nf} | "
        f"Pedido {pedido['pedido_id']} | "
        f"Cliente: {pedido['cliente']} | "
        f"R$ {pedido['total']:.2f} | "
        f"Acumulado: R$ {total_faturado:.2f} ({nfs_emitidas} NFs)"
    )

    # PONTO CRÍTICO: se o processo morrer aqui, antes do ack,
    # a mensagem será reentregue — causando NF duplicada.
    # Solução: idempotency key (pedido_id) no banco de dados.
    channel.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()

    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="fanout", durable=True)
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=processar_pedido)

    print(f"[Faturamento] Aguardando pedidos na fila '{QUEUE_NAME}'...")
    print(f"[Faturamento] Emitindo notas fiscais em tempo real.")
    print(f"[Faturamento] Pressione Ctrl+C para encerrar.\n")

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print(f"\n[Faturamento] Encerrado.")
        print(f"[Faturamento] NFs emitidas: {nfs_emitidas} | Total faturado: R$ {total_faturado:.2f}")
        channel.stop_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
