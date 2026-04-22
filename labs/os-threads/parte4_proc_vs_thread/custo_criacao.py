import threading
import multiprocessing
import time
import statistics

N = 200


def tarefa_vazia():
    pass


def medir_threads(n: int) -> list[float]:
    tempos = []
    threads = []
    for _ in range(n):
        t = threading.Thread(target=tarefa_vazia)
        inicio = time.perf_counter()
        t.start()
        fim = time.perf_counter()
        tempos.append((fim - inicio) * 1000)
        threads.append(t)
    for t in threads:
        t.join()
    return tempos


def medir_processos(n: int) -> list[float]:
    tempos = []
    processos = []
    for _ in range(n):
        p = multiprocessing.Process(target=tarefa_vazia)
        inicio = time.perf_counter()
        p.start()
        fim = time.perf_counter()
        tempos.append((fim - inicio) * 1000)
        processos.append(p)
    for p in processos:
        p.join()
    return tempos


def resumo(label: str, tempos: list[float]):
    print(f"\n=== {label} ===")
    print(f"  Amostras:      {len(tempos)}")
    print(f"  Média:         {statistics.mean(tempos):.3f} ms")
    print(f"  Mediana:       {statistics.median(tempos):.3f} ms")
    print(f"  Desvio padrão: {statistics.stdev(tempos):.3f} ms")
    print(f"  Mínimo:        {min(tempos):.3f} ms")
    print(f"  Máximo:        {max(tempos):.3f} ms")


if __name__ == '__main__':
    print(f"Medindo custo de criação com N={N}...")

    t_threads = medir_threads(N)
    resumo("Threads", t_threads)

    t_processos = medir_processos(N)
    resumo("Processos", t_processos)

    razao = statistics.mean(t_processos) / statistics.mean(t_threads)
    print(f"\nProcessos são {razao:.1f}× mais caros que threads (teoria: ~11×)")
