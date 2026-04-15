"""
Produtor — Gerador de Pedidos
==============================
Publica pedidos em um exchange do tipo fanout.
Todos os consumidores vinculados recebem uma cópia de cada pedido.

Padrão: Pub/Sub (publish-subscribe)
Exchange: fanout (broadcast para todas as filas vinculadas)
"""

import pika
import json
import time
import random
import uuid
from datetime import datetime

RABBITMQ_URL = "amqp://admin:admin123@localhost:5672/"
EXCHANGE_NAME = "pedidos"

PRODUTOS = [
    {"id": "P001", "nome": "Notebook Dell XPS 15",  "preco": 4999.90},
    {"id": "P002", "nome": "Mouse Logitech MX Master", "preco": 299.90},
    {"id": "P003", "nome": "Teclado Mecânico Keychron", "preco": 450.00},
    {"id": "P004", "nome": "Monitor LG UltraWide 34\"", "preco": 2800.00},
    {"id": "P005", "nome": "Headset Sony WH-1000XM5", "preco": 1200.00},
    {"id": "P006", "nome": "Webcam Logitech C920",    "preco": 380.00},
    {"id": "P007", "nome": "SSD Samsung 1TB NVMe",   "preco": 550.00},
]

CLIENTES = [f"cliente_{i:03d}" for i in range(100, 130)]


def criar_pedido() -> dict:
    """Cria um pedido aleatório simulando um cliente comprando um produto."""
    produto = random.choice(PRODUTOS)
    quantidade = random.randint(1, 5)
    return {
        "pedido_id":  str(uuid.uuid4())[:8].upper(),
        "timestamp":  datetime.now().isoformat(),
        "cliente":    random.choice(CLIENTES),
        "produto":    produto,
        "quantidade": quantidade,
        "total":      round(produto["preco"] * quantidade, 2),
        "status":     "NOVO",
    }


def conectar_com_retry(url: str, tentativas: int = 5) -> pika.BlockingConnection:
    """Tenta conectar ao RabbitMQ, aguardando se o broker ainda não estiver pronto."""
    for i in range(1, tentativas + 1):
        try:
            print(f"[Produtor] Conectando ao RabbitMQ... (tentativa {i}/{tentativas})")
            conn = pika.BlockingConnection(pika.URLParameters(url))
            print("[Produtor] Conectado com sucesso!")
            return conn
        except pika.exceptions.AMQPConnectionError:
            if i < tentativas:
                print(f"[Produtor] Broker não disponível. Aguardando 3s...")
                time.sleep(3)
            else:
                raise RuntimeError("Não foi possível conectar ao RabbitMQ. Verifique se o Docker está rodando.")


def main():
    connection = conectar_com_retry(RABBITMQ_URL)
    channel = connection.channel()

    # -----------------------------------------------------------------
    # Declara o exchange do tipo fanout (pub/sub)
    # durable=True: o exchange sobrevive a restart do broker
    # -----------------------------------------------------------------
    channel.exchange_declare(
        exchange=EXCHANGE_NAME,
        exchange_type="fanout",
        durable=True,
    )

    print(f"\n[Produtor] Exchange '{EXCHANGE_NAME}' (fanout) declarado.")
    print("[Produtor] Gerando pedidos a cada 1–3 segundos... Pressione Ctrl+C para parar.\n")
    print("-" * 65)

    pedidos_publicados = 0
    try:
        while True:
            pedido = criar_pedido()
            mensagem = json.dumps(pedido, ensure_ascii=False)

            # -----------------------------------------------------------------
            # Publica no exchange (routing_key="" é ignorado pelo fanout)
            # delivery_mode=2: mensagem persistente (salva em disco)
            # -----------------------------------------------------------------
            channel.basic_publish(
                exchange=EXCHANGE_NAME,
                routing_key="",
                body=mensagem,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type="application/json",
                ),
            )

            pedidos_publicados += 1
            print(
                f"[Produtor #{pedidos_publicados:04d}] "
                f"Pedido {pedido['pedido_id']} | "
                f"{pedido['cliente']} | "
                f"{pedido['produto']['nome']} x{pedido['quantidade']} | "
                f"R$ {pedido['total']:.2f}"
            )

            time.sleep(random.uniform(1.0, 3.0))

    except KeyboardInterrupt:
        print(f"\n[Produtor] Encerrado. Total publicado: {pedidos_publicados} pedidos.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
