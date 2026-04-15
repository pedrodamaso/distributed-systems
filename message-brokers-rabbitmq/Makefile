.PHONY: up down logs status install producer estoque email faturamento dlq painel clean

# ─────────────────────────────────────────────
#  Infraestrutura
# ─────────────────────────────────────────────

up:                          ## Sobe o RabbitMQ em background
	docker compose up -d
	@echo ""
	@echo "RabbitMQ iniciando... aguarde ~10s"
	@echo "Painel: http://localhost:15672 (admin / admin123)"

down:                        ## Para e remove containers
	docker compose down

logs:                        ## Acompanha logs do RabbitMQ
	docker compose logs -f rabbitmq

status:                      ## Verifica saúde do RabbitMQ
	docker compose ps
	@docker exec rabbitmq rabbitmq-diagnostics ping 2>/dev/null \
		&& echo "RabbitMQ: SAUDÁVEL" \
		|| echo "RabbitMQ: ainda iniciando..."

install:                     ## Instala dependências Python
	pip install -r requirements.txt

# ─────────────────────────────────────────────
#  Serviços
# ─────────────────────────────────────────────

producer:                    ## Inicia o produtor de pedidos
	python producer.py

estoque:                     ## Inicia o consumidor de estoque
	python consumer_estoque.py

email:                       ## Inicia o consumidor de email
	python consumer_email.py

faturamento:                 ## Inicia o consumidor de faturamento
	python consumer_faturamento.py

dlq:                         ## (Bônus) Inicia consumidor com DLQ
	python consumer_dlq.py

painel:                      ## Abre o painel de administração no browser
	xdg-open http://localhost:15672 2>/dev/null || open http://localhost:15672

# ─────────────────────────────────────────────
#  Experimentos
# ─────────────────────────────────────────────

# Experimento A: derruba o serviço de email e deixa acumular mensagens
experimento-a-derrubar:      ## Para o consumer_email (acumula msgs na fila)
	@echo "⚠ Mate o consumer_email.py com Ctrl+C e observe a fila_email no painel."
	@echo "  Após 30s, reinicie com: make email"

# Experimento B: derruba e restaura o broker
experimento-b-derrubar:      ## Para o RabbitMQ (testa durabilidade)
	docker compose stop rabbitmq
	@echo "RabbitMQ parado. Reinicie com: make experimento-b-restaurar"

experimento-b-restaurar:     ## Restaura o RabbitMQ e verifica persistência
	docker compose start rabbitmq
	@echo "RabbitMQ reiniciado. Verifique se as filas e mensagens persistiram."

# ─────────────────────────────────────────────
#  Limpeza
# ─────────────────────────────────────────────

clean:                       ## Remove containers e volumes (apaga dados)
	docker compose down -v
	@echo "Containers e volumes removidos."

help:                        ## Mostra este help
	@grep -E '^[a-zA-Z_-]+:.*?##.*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}'
