import socket
import threading
import time
import statistics
import sys


def enviar_pedido(host: str, port: int) -> float:
    """Envia um pedido e retorna a latência em ms."""
    start = time.perf_counter()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(b"pedido\n")
        s.recv(16)
    return (time.perf_counter() - start) * 1000


def benchmark(host: str, port: int, num_clientes: int, pedidos_por_cliente: int) -> dict:
    latencias = []
    erros = 0
    lock = threading.Lock()

    def cliente():
        nonlocal erros
        for _ in range(pedidos_por_cliente):
            try:
                lat = enviar_pedido(host, port)
                with lock:
                    latencias.append(lat)
            except Exception:
                with lock:
                    erros += 1

    inicio = time.perf_counter()
    threads = [threading.Thread(target=cliente) for _ in range(num_clientes)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    duracao = time.perf_counter() - inicio

    total_req = len(latencias)
    latencias_sorted = sorted(latencias)

    def percentil(p):
        if not latencias_sorted:
            return 0.0
        idx = int(len(latencias_sorted) * p / 100)
        idx = min(idx, len(latencias_sorted) - 1)
        return latencias_sorted[idx]

    return {
        "throughput_rps": total_req / duracao if duracao > 0 else 0,
        "latencia_media_ms": statistics.mean(latencias) if latencias else 0,
        "latencia_p50_ms": percentil(50),
        "latencia_p95_ms": percentil(95),
        "latencia_p99_ms": percentil(99),
        "erros": erros,
    }


def main():
    port_pool = 5001
    port_pedido = 5002

    cenarios = [
        (1, 10),
        (4, 10),
        (8, 10),
        (16, 10),
        (32, 10),
    ]

    print(f"{'Clientes':<10} {'Servidor':<15} {'Throughput (req/s)':<22} {'Lat. Média (ms)':<18} {'Lat. P95 (ms)'}")
    print("-" * 85)

    for num_clientes, ppc in cenarios:
        for label, port in [("Pool", port_pool), ("Por Pedido", port_pedido)]:
            try:
                resultado = benchmark('127.0.0.1', port, num_clientes, ppc)
                print(
                    f"{num_clientes:<10} {label:<15} "
                    f"{resultado['throughput_rps']:<22.1f} "
                    f"{resultado['latencia_media_ms']:<18.1f} "
                    f"{resultado['latencia_p95_ms']:.1f}"
                )
            except Exception as e:
                print(f"{num_clientes:<10} {label:<15} ERRO: {e}")


if __name__ == '__main__':
    # Suba ambos os servidores antes de rodar este script
    # Terminal 1: python parte1_pool/server.py
    # Terminal 2: python parte2_por_pedido/server.py
    main()
