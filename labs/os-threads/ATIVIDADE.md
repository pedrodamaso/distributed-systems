# Laboratório Guiado — Threads, Servidores Concorrentes e Custo de Invocação

## Metadados

- **Tipo**: Laboratório Guiado
- **Nível**: Intermediário
- **Tempo estimado**: 3–4 horas
- **Pré-requisitos**: Capítulo 7 (Sistema Operacional), Python básico, conceitos de socket e thread
- **Conceitos abordados**: Processos vs. threads, arquiteturas de servidor multithreaded (pool, por pedido, por conexão), custos de invocação, sincronização, cópia na escrita
- **Linguagem/Ferramentas**: Python 3.10+, biblioteca padrão (`socket`, `threading`, `multiprocessing`, `time`)

---

## Contexto e Motivação

Um time de engenharia da **DataStream Inc.** precisa escolher a arquitetura interna de um servidor de processamento de imagens. Cada pedido recebido pela rede leva ~2 ms de CPU e ~8 ms simulando acesso a um banco de dados (E/S). O time debate:

- "Precisamos de um pool fixo de threads? Ou criamos uma thread por pedido?"
- "Vale a pena usar processos separados? E o custo de criar processos?"
- "Por que RPC entre processos no mesmo host é tão mais lento que uma chamada local?"

Este laboratório reproduz esse cenário em pequena escala para que você meça, com dados reais, as diferenças preditas pela teoria do Capítulo 7.

---

## Objetivos de Aprendizado

Ao final deste laboratório, você será capaz de:

1. Implementar um servidor TCP com arquitetura de **pool de trabalhadores** e compará-lo ao de **thread por pedido**
2. Medir empiricamente o impacto do número de threads no **throughput** do servidor
3. Comparar o custo de criação de **threads** vs. **processos**
4. Explicar por que a invocação entre dois processos no mesmo host é mais cara que uma chamada dentro do mesmo processo
5. Demonstrar o efeito do **copy-on-write** no `fork()`

---

## Estrutura do Repositório Esperada

```
os-threads-e-invocacao/
├── ATIVIDADE.md          ← este arquivo
├── parte1_pool/
│   ├── server.py         ← implementado
│   └── client.py         ← implementado (use também para testar a Parte 2: python parte1_pool/client.py 5002)
├── parte2_por_pedido/
│   └── server.py         ← implementado
├── parte3_benchmark/
│   └── benchmark.py      ← implementado
├── parte4_proc_vs_thread/
│   └── custo_criacao.py  ← implementado
├── parte5_cow/
│   └── demo_cow.py       ← implementado
└── reflexao.md           ← suas respostas às perguntas
```

---

## Parte 1 — Servidor com Pool de Trabalhadores

### Conceito

No modelo **pool de trabalhadores**, N threads são criadas uma única vez na inicialização. Pedidos chegam, são enfileirados, e qualquer thread livre os consome. Isso evita o custo de criar/destruir threads a cada pedido.

```
Clientes → [Fila de pedidos] → Thread-1
                             → Thread-2
                             → Thread-N
```

### Tarefa

Implemente `parte1_pool/server.py` usando o esqueleto abaixo.

```python
# parte1_pool/server.py
import socket
import threading
import queue
import time

HOST = '0.0.0.0'
PORT = 5001
POOL_SIZE = 4        # número fixo de threads trabalhadoras
REQUEST_QUEUE = queue.Queue(maxsize=100)

def simular_trabalho():
    """Simula 2ms de CPU + 8ms de E/S."""
    # CPU bound
    end = time.perf_counter() + 0.002
    while time.perf_counter() < end:
        pass
    # I/O bound (E/S simulada com sleep)
    time.sleep(0.008)

def worker(thread_id: int):
    """
    TODO: loop infinito que:
      1. Retira um item de REQUEST_QUEUE (bloqueante)
      2. Lê os dados do socket recebido
      3. Chama simular_trabalho()
      4. Envia resposta "OK\n" ao cliente
      5. Fecha o socket
    """
    raise NotImplementedError

def main():
    """
    TODO:
      1. Crie POOL_SIZE threads daemon chamando worker(i)
      2. Inicie todas as threads
      3. Abra socket TCP, aceite conexões em loop
      4. Para cada conexão aceita, coloque (conn, addr) em REQUEST_QUEUE
    """
    raise NotImplementedError

if __name__ == '__main__':
    main()
```

**Cliente fornecido** — salve como `parte1_pool/client.py` (não precisa modificar):

```python
# parte1_pool/client.py
import socket
import sys

HOST = '127.0.0.1'
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5001

def enviar_pedido():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b"pedido\n")
        resposta = s.recv(16)
        return resposta

if __name__ == '__main__':
    r = enviar_pedido()
    print(f"Resposta: {r.decode().strip()}")
```

### Verificação da Parte 1

Execute em dois terminais:

```bash
# Terminal 1
python parte1_pool/server.py

# Terminal 2 — deve imprimir "Resposta: OK"
python parte1_pool/client.py
```

---

## Parte 2 — Servidor Thread por Pedido

### Conceito

Nesta arquitetura, cada pedido recebido dispara a **criação de uma nova thread**, que termina ao concluir o pedido. Não há limite fixo de threads — o servidor é mais elástico, mas paga o custo de criação/destruição a cada pedido.

### Tarefa

Implemente `parte2_por_pedido/server.py`:

```python
# parte2_por_pedido/server.py
import socket
import threading
import time

HOST = '0.0.0.0'
PORT = 5002

def simular_trabalho():
    """Simula 2ms de CPU + 8ms de E/S."""
    end = time.perf_counter() + 0.002
    while time.perf_counter() < end:
        pass
    time.sleep(0.008)

def handle_client(conn, addr):
    """
    TODO: leia os dados, chame simular_trabalho(),
    responda "OK\n" e feche o socket.
    A thread deve encerrar após processar um pedido.
    """
    raise NotImplementedError

def main():
    """
    TODO: aceite conexões em loop e, para cada uma,
    crie e inicie uma nova thread daemon apontando para handle_client.
    """
    raise NotImplementedError

if __name__ == '__main__':
    main()
```

### Verificação da Parte 2

```bash
# Terminal 1
python parte2_por_pedido/server.py

# Terminal 2 — reutiliza o cliente da Parte 1, passando a porta como argumento
python parte1_pool/client.py 5002
```

---

## Parte 3 — Benchmark: Throughput × Número de Clientes Concorrentes

### Conceito

Com 2 ms de CPU e 8 ms de E/S por pedido:

- 1 thread → máximo teórico = 1000 ms / 10 ms = **100 req/s**
- N threads (limitado por E/S) → máximo teórico ≈ **500 req/s**
- N threads (limitado por CPU) → máximo teórico ≈ **400 req/s** (com cache 75%)

Você vai medir o throughput real e comparar com a teoria.

### Tarefa

Complete `parte3_benchmark/benchmark.py`:

```python
# parte3_benchmark/benchmark.py
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
    """
    TODO: dispare `num_clientes` threads simultaneamente,
    cada uma fazendo `pedidos_por_cliente` chamadas a enviar_pedido().
    Colete todas as latências e calcule:
      - throughput (req/s)
      - latência média, p50, p95, p99 (ms)
      - total de erros
    Retorne um dict com essas métricas.
    """
    raise NotImplementedError

def main():
    port_pool     = 5001
    port_pedido   = 5002

    cenarios = [
        (1,  10),    # 1 cliente, 10 pedidos cada
        (4,  10),    # 4 clientes simultâneos
        (8,  10),    # 8 clientes simultâneos
        (16, 10),    # 16 clientes simultâneos
        (32, 10),    # 32 clientes simultâneos
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
```

### O que observar

- Com 1 cliente serial, os dois servidores devem ter throughput semelhante (~100 req/s)
- Com muitos clientes simultâneos, observe qual arquitetura satura primeiro
- Compare a latência P95 — o pool pode ter maior P95 quando a fila enche

---

## Parte 4 — Custo de Criação: Thread vs. Processo

### Conceito

Da teoria (seção 7.3.6):

| | Criação | Troca de contexto |
|---|---|---|
| Thread | ~1 ms | ~0,04–0,4 ms |
| Processo | ~11 ms | ~1,8 ms |

Você vai medir isso diretamente em Python.

### Tarefa

Implemente `parte4_proc_vs_thread/custo_criacao.py`:

```python
# parte4_proc_vs_thread/custo_criacao.py
import threading
import multiprocessing
import time
import statistics

N = 200  # número de threads/processos a criar

def tarefa_vazia():
    """Não faz nada — usada apenas para medir custo de criação."""
    pass

def medir_threads(n: int) -> list[float]:
    """
    TODO: crie e inicie `n` threads apontando para tarefa_vazia().
    Meça o tempo de criação + start de cada uma (não inclua o join).
    Retorne lista de tempos em ms.
    Dica: use time.perf_counter() imediatamente antes e depois de thread.start()
    """
    raise NotImplementedError

def medir_processos(n: int) -> list[float]:
    """
    TODO: igual a medir_threads, mas usando multiprocessing.Process.
    IMPORTANTE: faça join() de todos após coletar os tempos,
    para não deixar processos zumbis.
    """
    raise NotImplementedError

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
```

---

## Parte 5 — Demonstração do Copy-on-Write no fork()

### Conceito

Quando `fork()` é chamado, o SO não copia imediatamente as páginas de memória do processo pai. Em vez disso, pai e filho compartilham as mesmas páginas físicas marcadas como *somente leitura*. A cópia ocorre apenas na primeira escrita em cada página — daí o nome **copy-on-write**.

### Tarefa

Implemente `parte5_cow/demo_cow.py`:

```python
# parte5_cow/demo_cow.py
import os
import time
import sys

TAMANHO_MB = 100
PAGINA = 4096  # bytes por página (típico em x86)

def alocar_dados(tamanho_mb: int) -> bytearray:
    """Aloca um bloco de memória e inicializa com zeros."""
    return bytearray(tamanho_mb * 1024 * 1024)

def medir_fork_sem_escrita(dados: bytearray) -> float:
    """
    TODO:
    1. Registre o tempo antes do fork()
    2. Faça fork()
    3. No processo filho: registre o tempo logo após fork(), imprima,
       e termine com os.exit(0) — NÃO escreva nos dados
    4. No processo pai: faça waitpid() e retorne o tempo total do fork
    Retorne o tempo em ms (medido no pai, do fork() ao waitpid()).
    """
    raise NotImplementedError

def medir_fork_com_escrita(dados: bytearray) -> float:
    """
    TODO: igual ao anterior, mas o filho deve escrever em TODAS as páginas:
        for i in range(0, len(dados), PAGINA):
            dados[i] = 1
    Isso força a cópia física de cada página (copy-on-write disparado).
    """
    raise NotImplementedError

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
```

---

## Critérios de Avaliação

| Critério | Peso | Descrição |
|---|---|---|
| **Parte 1 — Pool de trabalhadores funcional** | 20% | Servidor responde corretamente com POOL_SIZE threads; fila funciona |
| **Parte 2 — Thread por pedido funcional** | 15% | Servidor cria nova thread por pedido; responde corretamente |
| **Parte 3 — Benchmark completo** | 25% | Coleta dados reais; tabela preenchida; conclusão sobre qual escala melhor |
| **Parte 4 — Custo de criação medido** | 20% | Implementação correta; razão thread/processo plausível (5–15×) |
| **Parte 5 — Demo copy-on-write** | 10% | Fork sem escrita notavelmente mais rápido que fork com escrita |
| **Reflexão crítica** | 10% | Perguntas respondidas conectando dados medidos à teoria do capítulo |

---

## Perguntas de Reflexão

Responda em `reflexao.md` com base nos dados que você mediu (não apenas na teoria).

1. **Throughput observado vs. teórico**: com 2 ms de CPU e 8 ms de E/S, a teoria prevê 100 req/s com 1 thread e ~500 req/s com N threads (gargalo de E/S). Seus dados confirmam essa previsão? Se não, o que pode explicar a diferença?

2. **Pool vs. por pedido**: em qual cenário (poucos ou muitos clientes simultâneos) a diferença de latência P95 entre as duas arquiteturas foi mais expressiva? Por que o pool tem latência mais previsível que o modelo por pedido sob alta carga?

3. **Custo de criação**: a razão que você mediu entre criar um processo e criar uma thread foi próxima dos ~11× citados no livro? Qual implicação isso tem para servidores que recebem rajadas de pedidos (ex.: Black Friday)?

4. **Copy-on-write**: seus resultados mostram que escrever em todas as páginas após o fork é muito mais caro que o fork em si. Relacione isso com o uso de CoW em containers Docker: por que camadas de imagem Docker são eficientes mesmo quando vários containers rodam a mesma imagem?

5. **Trade-off arquitetural**: imagine que o servidor precisa agora processar pedidos que levam tempos muito variáveis (alguns 5 ms, outros 2 segundos). O pool de tamanho fixo ainda é a melhor escolha? Qual arquitetura do Capítulo 7 seria mais adequada e por quê?

---

## Dicas e Armadilhas Comuns

- **`queue.Queue` é thread-safe** — não adicione locks extras; ela já sincroniza internamente.
- **Threads daemon**: use `thread.daemon = True` antes de `thread.start()` para que o programa encerre quando o processo principal terminar.
- **`time.sleep()` libera a GIL** do Python, o que faz a simulação de E/S ser genuinamente concorrente entre threads — isso é essencial para que o benchmark faça sentido.
- **Armadilha do benchmark**: se o servidor ainda não subiu quando o benchmark começa, você terá erros de conexão. Adicione um `time.sleep(0.5)` no início do benchmark ou implemente retry.
- **`multiprocessing` no Windows**: a função `tarefa_vazia` deve ser definida no top-level do módulo (não dentro de outra função) para que o Windows consiga serializá-la com `pickle`.
- **`fork()` só existe em Unix/Linux/macOS** — a Parte 5 não funciona no Windows. Se necessário, use WSL.
- **GIL e paralelismo real**: threads Python não executam código CPU-bound em paralelo real (por causa do GIL). O ganho de throughput no benchmark vem do fato de que `time.sleep()` (E/S simulada) libera o GIL — exatamente como E/S real faria.

---

## Referências

- COULOURIS, G. et al. *Sistemas Distribuídos: Conceitos e Projeto*. 5. ed. Bookman, 2013. Seções 7.3 e 7.4.
- Anderson, T. et al. *Scheduler Activations: Effective Kernel Support for the User-Level Management of Parallelism*. SOSP 1991.
- Bershad, B. et al. *Lightweight Remote Procedure Call*. SOSP 1989.
- Documentação Python: [`threading`](https://docs.python.org/3/library/threading.html), [`multiprocessing`](https://docs.python.org/3/library/multiprocessing.html), [`queue`](https://docs.python.org/3/library/queue.html)
