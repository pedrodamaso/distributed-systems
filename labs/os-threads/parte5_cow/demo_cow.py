import os
import time
import sys

TAMANHO_MB = 100
PAGINA = 4096


def alocar_dados(tamanho_mb: int) -> bytearray:
    return bytearray(tamanho_mb * 1024 * 1024)


def medir_fork_sem_escrita(dados: bytearray) -> float:
    inicio = time.perf_counter()
    pid = os.fork()
    if pid == 0:
        # filho: encerra sem escrever
        os._exit(0)
    else:
        os.waitpid(pid, 0)
        return (time.perf_counter() - inicio) * 1000


def medir_fork_com_escrita(dados: bytearray) -> float:
    inicio = time.perf_counter()
    pid = os.fork()
    if pid == 0:
        # filho: escreve em todas as páginas, disparando CoW
        for i in range(0, len(dados), PAGINA):
            dados[i] = 1
        os._exit(0)
    else:
        os.waitpid(pid, 0)
        return (time.perf_counter() - inicio) * 1000


if __name__ == '__main__':
    print(f"Alocando {TAMANHO_MB} MB de dados...")
    dados = alocar_dados(TAMANHO_MB)
    print(f"Dados alocados: {len(dados) / (1024*1024):.0f} MB\n")

    t_sem = medir_fork_sem_escrita(dados)
    print(f"fork() SEM escrita (CoW não disparado): {t_sem:.2f} ms")

    t_com = medir_fork_com_escrita(dados)
    print(f"fork() COM escrita (CoW disparado):      {t_com:.2f} ms")

    print(f"\nEscrever em todas as páginas foi {t_com/t_sem:.1f}× mais lento.")
    print("Isso demonstra que o fork() real é barato — o custo está nas escritas.")
