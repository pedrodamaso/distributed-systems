# Lab: Threads, Servidores Concorrentes e Custo de Invocação

Laboratório guiado do Capítulo 7 (Sistema Operacional) de Sistemas Distribuídos.

## Pré-requisitos

- Python 3.10+
- Linux/macOS (Parte 5 requer `fork()`)

## Como executar

### Partes 1 e 2 — Servidores

```bash
# Pool de trabalhadores (porta 5001)
python parte1_pool/server.py

# Thread por pedido (porta 5002)
python parte2_por_pedido/server.py

# Testar manualmente
python parte1_pool/client.py        # porta 5001 (Pool)
python parte1_pool/client.py 5002   # porta 5002 (Por Pedido) — mesmo cliente, porta diferente
```

### Parte 3 — Benchmark

Com ambos os servidores rodando:

```bash
python parte3_benchmark/benchmark.py
```

### Parte 4 — Custo de criação

```bash
python parte4_proc_vs_thread/custo_criacao.py
```

### Parte 5 — Copy-on-write

```bash
python parte5_cow/demo_cow.py
```

## Entrega

- Código implementado em cada arquivo `*.py` ✓
- `reflexao.md` preenchido com dados medidos e análise

## Referência

Coulouris et al., *Sistemas Distribuídos*, 5. ed., Capítulo 7 (seções 7.3 e 7.4).
