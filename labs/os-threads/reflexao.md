# Reflexão — Laboratório: Threads, Servidores Concorrentes e Custo de Invocação

**Nome:**
**Data:**

---

## Resultados Medidos

### Parte 3 — Tabela de Benchmark

<!-- Cole aqui a saída do benchmark.py -->

```
Clientes   Servidor        Throughput (req/s)     Lat. Média (ms)    Lat. P95 (ms)
```

### Parte 4 — Custo de Criação

| | Média (ms) | Mediana (ms) | Desvio padrão (ms) |
|---|---|---|---|
| Thread | | | |
| Processo | | | |
| Razão (processo/thread) | | | |

### Parte 5 — Copy-on-Write

| Cenário | Tempo (ms) |
|---|---|
| fork() sem escrita (CoW não disparado) | |
| fork() com escrita em todas as páginas | |
| Razão | |

---

## Perguntas de Reflexão

### 1. Throughput observado vs. teórico

<!-- Sua resposta aqui -->

### 2. Pool vs. thread por pedido

<!-- Sua resposta aqui -->

### 3. Custo de criação de thread vs. processo

<!-- Sua resposta aqui -->

### 4. Copy-on-write e containers Docker

<!-- Sua resposta aqui -->

### 5. Trade-off arquitetural com pedidos de tempo variável

<!-- Sua resposta aqui -->
