# Trabalho Teórico — Capítulo 8: Objetos e Componentes Distribuídos

## Instruções Gerais

- Responda todas as questões com base nos conceitos estudados no Capítulo 8.
- Justifique suas respostas — não é suficiente apenas citar nomes ou termos; demonstre compreensão.
- Nas questões comparativas, use tabelas ou estrutura clara para facilitar a leitura.
- As questões estão organizadas em partes progressivas: conceituação → análise → síntese.

---

## Parte 1 — Objetos Distribuídos: Conceitos e Diferenças 

### Questão 1.1 — Comparação conceitual 

Preencha a tabela abaixo identificando o equivalente distribuído de cada conceito local de OO, e escreva uma frase explicando **o que muda** em cada caso no contexto distribuído:

| Conceito local (OO) | Equivalente distribuído | O que muda no contexto distribuído? |
|---|---|---|
| Referência de objeto | | |
| Interface | | |
| Exceção | | |
| Coleta de lixo | | |

---

## Parte 2 — CORBA: Arquitetura e IDL 

### Questão 2.1 — Papéis na arquitetura CORBA 

Para cada componente da arquitetura CORBA listado abaixo, escreva **duas a três frases** descrevendo sua função e como ele se relaciona com os demais:

| Componente | Função e relação com os demais |
|---|---|
| ORB (Object Request Broker) | |
| POA (Portable Object Adapter) | |
| Repositório de Interfaces | |
| Repositório de Implementações | |
| IOR Persistente | |

---

### Questão 2.3 — IOR: transiente vs. persistente 

Uma empresa de e-commerce possui dois serviços:

- **Serviço de Sessão de Compra**: representa o carrinho de um usuário durante uma visita ao site. Quando o usuário fecha o navegador, o carrinho é descartado.
- **Serviço de Catálogo de Produtos**: repositório central de produtos acessado por todos os clientes e sistemas internos da empresa. Deve estar disponível mesmo após reinicializações do servidor.

a) Para cada serviço, indique qual tipo de IOR (transiente ou persistente) é mais adequado e **justifique** com base nas características de cada tipo. 

b) O que acontece quando um cliente tenta usar uma **IOR persistente** e o servidor ainda não está em execução? Que componente da arquitetura CORBA é responsável por resolver essa situação? 

### Questão 2.4 — IDL

a) Por que a IDL é necessária em um sistema CORBA multilíngue, diferentemente de RMI Java que usa interfaces nativas da linguagem?

b) Qual é o papel do compilador de IDL na geração de artefatos de código (stubs, skeletons, helpers)?

c) Diferencie os parâmetros in, out e inout em uma assinatura de método IDL e identifique uma limitação dessa semântica ao mapear para Java.

---

## Parte 3 — De Objetos a Componentes

### Questão 3.1 — Motivação para componentes

O texto apresenta quatro problemas do middleware orientado a objetos que motivaram a criação do modelo de componentes.

Para **cada um dos quatro problemas**, complete a tabela:

| Problema | Descrição com suas palavras | Exemplo concreto em um sistema de SI |
|---|---|---|
| Dependências implícitas | | |
| Interação com o middleware | | |
| Aspectos não funcionais misturados | | |
| Sem suporte a implantação | | |

> **Dica para os exemplos:** pense em um sistema de vendas online, um sistema bancário ou um sistema de RH.

---

## Parte 4 — EJB e Fractal: Estudo Comparativo (25 pontos)

### Questão 4.1 — Tabela comparativa EJB × Fractal

Complete a tabela comparativa com base nos conhecimentos adquiridos:

| Critério | EJB 3.0 | Fractal |
|---|---|---|
| Peso do framework | | |
| Linguagem(ns) suportada(s) | | |
| Como aspectos não funcionais são gerenciados | | |
| Suporte a reconfiguração em tempo de execução | | |
| Caso de uso típico (dê um exemplo de sistema real) | | |

---

*Referência: COULOURIS, G. et al. **Sistemas Distribuídos: Conceitos e Projeto**. 5. ed. Porto Alegre: Bookman, 2013. Cap. 8.*
