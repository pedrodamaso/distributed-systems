# Atividade Prática — Capítulo 9: Serviços Web

**Disciplina:** Sistemas Distribuídos  
**Referência:** Coulouris et al., *Sistemas Distribuídos*, Cap. 9

---

## Prática 1 — Explorando uma API REST Real

### Título e Tipo
Laboratório de Exploração: Consumindo uma API REST pública com análise de mensagens HTTP/JSON.

### Objetivo Pedagógico
Conectar o conceito teórico de serviços Web (URI, requisição-resposta, representação de dados) com a experiência concreta de interagir com um serviço Web real usando a estratégia REST.

### Contextualização do Problema
Uma empresa de SI precisa integrar dados de localização de municípios brasileiros em seu sistema. O IBGE disponibiliza uma API REST pública com dados oficiais. Sua tarefa é explorar esse serviço, documentar sua interface e consumir suas operações.

### Recursos Necessários
- Computador com acesso à Internet.
- Ferramenta de cliente HTTP: `curl` (terminal), [Postman](https://www.postman.com/) ou extensão Thunder Client (VS Code).
- Editor de texto ou IDE.
- Opcional: Python 3 com a biblioteca `requests`.

### Passo a Passo

**Parte 1 — Descoberta do serviço (20 min)**

1. Acesse a documentação da API do IBGE: `https://servicodados.ibge.gov.br/api/docs/localidades`

2. Identifique e anote:
   - A **URL base** do serviço.
   - Pelo menos **4 operações** disponíveis (recursos/endpoints).
   - O **formato de resposta** padrão.
   - Se há suporte a **múltiplos formatos** (JSON, XML).

3. Responda por escrito:
   - Esse serviço usa o estilo **REST** ou **SOAP**? Como você identificou?
   - Quais verbos HTTP são utilizados? O serviço é somente de leitura?

**Parte 2 — Consumindo o serviço (30 min)**

Execute as requisições abaixo usando `curl` ou Postman e registre as respostas:

```bash
# Listar todas as regiões do Brasil
curl -s "https://servicodados.ibge.gov.br/api/v1/localidades/regioes" | python3 -m json.tool

# Listar os estados de uma região (substitua {id} por 3 para a região Sudeste)
curl -s "https://servicodados.ibge.gov.br/api/v1/localidades/regioes/3/estados" | python3 -m json.tool

# Buscar um município específico por nome
curl -s "https://servicodados.ibge.gov.br/api/v1/localidades/municipios?nome=Vicosa" | python3 -m json.tool

# Solicitar a resposta em XML
curl -s -H "Accept: application/xml" "https://servicodados.ibge.gov.br/api/v1/localidades/regioes"
```

Para cada requisição, anote:
- O código de status HTTP retornado.
- A estrutura da resposta JSON (campos principais).
- O tempo de resposta (Postman mostra automaticamente).

**Parte 3 — Análise das mensagens (20 min)**

No Postman (ou com `curl -v`), inspecione os **cabeçalhos HTTP** de uma requisição e resposta. Identifique:

- O método HTTP usado (`GET`, `POST`, etc.).
- O cabeçalho `Content-Type` da resposta.
- O cabeçalho `Accept` da requisição.
- Quaisquer cabeçalhos relacionados a cache (`Cache-Control`, `ETag`).

Relacione cada elemento encontrado com os conceitos do Capítulo 9:
- URI como referência de serviço.
- HTTP como protocolo de transporte.
- XML/JSON como representação de dados.

**Parte 4 — Implementação (30 min)**

Implemente um script Python que:

1. Consulte todos os municípios de um estado escolhido pelo usuário (por sigla, ex: MG).
2. Exiba o total de municípios encontrados.
3. Liste os 10 primeiros municípios em ordem alfabética.

```python
import requests

def buscar_municipios_por_estado(sigla_uf):
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{sigla_uf}/municipios"
    resposta = requests.get(url)
    
    if resposta.status_code == 200:
        municipios = resposta.json()
        nomes = sorted([m['nome'] for m in municipios])
        print(f"Total de municípios em {sigla_uf}: {len(nomes)}")
        print("Primeiros 10:")
        for nome in nomes[:10]:
            print(f"  - {nome}")
    else:
        print(f"Erro: status {resposta.status_code}")

sigla = input("Digite a sigla do estado (ex: MG): ").upper()
buscar_municipios_por_estado(sigla)
```

### Entregáveis Esperados

1. **Relatório em texto** (máximo 1 página) contendo:
   - Respostas às perguntas das Partes 1 e 3.
   - Print ou colagem de pelo menos duas respostas JSON inspecionadas.
   - Tabela comparando o serviço explorado com os conceitos de SOAP/REST do capítulo.

2. **Código Python** da Parte 4, funcionando corretamente.

3. **Reflexão** (3–5 linhas): em que situação você usaria SOAP em vez desta API REST? O que estaria "faltando" nesta API para atender a esse cenário?

### Extensão Opcional — Desafio Avançado

Construa um serviço *mashup*: integre a API do IBGE com a API de previsão do tempo (Open-Meteo, gratuita e sem chave de API) para, dado o nome de um município, exibir a previsão do tempo dos próximos 3 dias.

Dica: a API do IBGE retorna latitude e longitude de cada município; a Open-Meteo usa essas coordenadas para fornecer a previsão.

---

## Prática 2 — Projetando e Documentando uma API com WSDL Simplificado

### Título e Tipo
Atividade de Projeto: Modelando o contrato de um serviço Web para um sistema de biblioteca universitária.

### Objetivo Pedagógico
Desenvolver a competência de especificar formalmente a interface de um serviço Web, compreendendo a estrutura de uma descrição WSDL e os padrões de troca de mensagens.

### Contextualização do Problema
A Biblioteca Central de uma universidade quer expor seus serviços para que sistemas de outros campi, bibliotecas parceiras e aplicativos de alunos possam consultar e reservar livros automaticamente.

### Recursos Necessários
- Editor de texto (VS Code, Notepad++ ou similar).
- Papel e caneta para rascunho (opcional).
- Opcional: ferramenta online para validar XML (ex: xmlvalidation.com).

### Passo a Passo

**Parte 1 — Levantamento de operações (15 min)**

Liste as operações que o serviço de biblioteca deve expor. Para cada uma, defina:

| Operação           | Entrada                        | Saída                              | Padrão WSDL |
|--------------------|-------------------------------|-------------------------------------|-------------|
| `buscarLivro`      | título ou ISBN (string)       | lista de livros disponíveis         | In-Out      |
| `verificarDisponibilidade` | ISBN (string)        | quantidade disponível (int)         | In-Out      |
| `reservarLivro`    | ISBN, matrícula aluno          | confirmação de reserva              | In-Out      |
| `cancelarReserva`  | código de reserva              | confirmação de cancelamento         | In-Out      |
| `notificarDisponibilidade` | e-mail, ISBN            | (notificação assíncrona)            | In-Only     |

Acrescente pelo menos **2 operações adicionais** que você julgue necessárias.

**Parte 2 — Definição de tipos (20 min)**

Escreva em pseudoXML (ou XML real) os tipos de dados complexos necessários:

```xml
<!-- Tipo: Livro -->
<complexType name="Livro">
  <element name="isbn"       type="string"/>
  <element name="titulo"     type="string"/>
  <element name="autor"      type="string"/>
  <element name="ano"        type="int"/>
  <element name="disponivel" type="int"/>
</complexType>

<!-- Tipo: Reserva -->
<complexType name="Reserva">
  <element name="codigoReserva" type="string"/>
  <element name="isbn"          type="string"/>
  <element name="matricula"     type="string"/>
  <element name="dataReserva"   type="date"/>
  <element name="dataVencimento" type="date"/>
</complexType>
```

Defina o tipo para **pelo menos mais um** elemento necessário (ex: `ResultadoBusca`, `Confirmacao`).

**Parte 3 — Estrutura WSDL (30 min)**

Preencha a estrutura WSDL abaixo para o serviço de biblioteca:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<description xmlns="http://www.w3.org/ns/wsdl"
             targetNamespace="http://biblioteca.universidade.edu.br/servicos"
             xmlns:tns="http://biblioteca.universidade.edu.br/servicos"
             xmlns:xsd="http://www.w3.org/2001/XMLSchema">

  <!-- SEÇÃO 1: Tipos de dados -->
  <types>
    <!-- Cole aqui os tipos definidos na Parte 2 -->
  </types>

  <!-- SEÇÃO 2: Mensagens -->
  <interface name="BibliotecaInterface">

    <!-- Operação buscarLivro -->
    <operation name="buscarLivro" pattern="http://www.w3.org/ns/wsdl/in-out">
      <input  messageLabel="In"  element="tns:BuscarLivroRequest"/>
      <output messageLabel="Out" element="tns:BuscarLivroResponse"/>
    </operation>

    <!-- Operação reservarLivro -->
    <operation name="reservarLivro" pattern="http://www.w3.org/ns/wsdl/in-out">
      <input  messageLabel="In"  element="tns:ReservarLivroRequest"/>
      <output messageLabel="Out" element="tns:ReservarLivroResponse"/>
    </operation>

    <!-- Operação notificarDisponibilidade (assíncrona) -->
    <operation name="notificarDisponibilidade" pattern="http://www.w3.org/ns/wsdl/in-only">
      <input messageLabel="In" element="tns:NotificacaoRequest"/>
    </operation>

    <!-- Adicione as demais operações aqui -->

  </interface>

  <!-- SEÇÃO 3: Vínculo (binding) -->
  <binding name="BibliotecaSOAPBinding"
           interface="tns:BibliotecaInterface"
           type="http://www.w3.org/ns/wsdl/soap"
           wsoap:protocol="http://www.w3.org/2003/05/soap/bindings/HTTP/">
  </binding>

  <!-- SEÇÃO 4: Serviço (endpoint) -->
  <service name="BibliotecaService"
           interface="tns:BibliotecaInterface">
    <endpoint name="BibliotecaEndpoint"
              binding="tns:BibliotecaSOAPBinding"
              address="http://biblioteca.universidade.edu.br/servicos/soap"/>
  </service>

</description>
```

**Parte 4 — Diagrama de interação (15 min)**

Desenhe (pode ser feito à mão ou com ferramenta simples) o diagrama de sequência para o cenário:

> Um sistema do campus B quer reservar o livro "Sistemas Distribuídos" (ISBN 978-0-13-239227-3) para o aluno de matrícula 12345.

O diagrama deve mostrar:
1. Sistema do campus B verifica disponibilidade.
2. Recebe resposta com quantidade disponível.
3. Faz a reserva.
4. Recebe confirmação.

### Entregáveis Esperados

1. **Tabela de operações** completa (Parte 1), com as 2 operações adicionais.
2. **Definições XML** de tipos de dados (Parte 2).
3. **Documento WSDL** preenchido (Parte 3), com todas as operações.
4. **Diagrama de sequência** da Parte 4 (pode ser foto de rascunho).
5. **Resposta escrita** (5 linhas): como o serviço UDDI seria usado por uma biblioteca parceira para descobrir e usar este serviço?

### Extensão Opcional — Desafio Avançado

Implemente um servidor Flask simples em Python que exponha 2 das operações projetadas (ex: `buscarLivro` e `verificarDisponibilidade`) como uma API REST, com respostas em JSON. Depois, escreva um cliente Python que consuma essa API. Documente a API usando o padrão OpenAPI (Swagger) e compare com a abordagem WSDL que você projetou: quais são as diferenças práticas?

---

## Prática 3 — Estudo de Caso: Projetando uma Arquitetura SOA

### Título e Tipo
Estudo de caso em grupo: Projeto de Arquitetura Orientada a Serviços para o sistema de uma empresa fictícia.

### Objetivo Pedagógico
Aplicar os conceitos de SOA, baixo acoplamento, descrição de serviços e coordenação para projetar uma arquitetura distribuída realista no contexto de Sistemas de Informação.

### Contextualização do Problema
A empresa **MercaFácil** é um e-commerce de médio porte que quer modernizar sua arquitetura. Atualmente, o sistema é um monólito. A empresa quer migrar para uma arquitetura SOA baseada em serviços Web, integrando:

- Catálogo de produtos (consulta e atualização de estoque).
- Carrinho de compras (adicionar, remover, calcular total).
- Pagamento (cartão de crédito, PIX, boleto).
- Logística (cálculo de frete, rastreamento).
- Notificações (e-mail, SMS para cliente).

### Recursos Necessários
- Grupos de 3 a 4 alunos.
- Papel flip-chart ou ferramenta de diagramação (draw.io, Excalidraw — gratuitos).
- Computador para pesquisa.

### Passo a Passo

**Fase 1 — Identificação dos serviços (20 min)**

Para cada área de negócio acima, defina:
- Nome do serviço Web.
- Pelo menos 3 operações expostas.
- Padrão de comunicação de cada operação (requisição-resposta ou assíncrono).

**Fase 2 — Diagrama de arquitetura (25 min)**

Crie um diagrama mostrando:
- Os 5 serviços Web da MercaFácil.
- Os fluxos de comunicação entre eles no cenário de uma compra completa.
- Indique quais comunicações são síncronas e quais são assíncronas.
- Posicione um serviço de diretório (UDDI) e um gateway de API (ponto de entrada unificado).

**Fase 3 — Coreografia do processo de compra (20 min)**

Descreva em texto estruturado (pode usar pseudocódigo ou lista numerada) a sequência de interações entre os serviços para o cenário:

> Cliente adiciona produto ao carrinho → finaliza pedido → pagamento aprovado → estoque atualizado → logística acionada → cliente notificado.

Para cada etapa, indique:
- Qual serviço é chamado.
- Qual operação é invocada.
- O que acontece em caso de falha (ex: pagamento recusado, produto sem estoque).

**Fase 4 — Segurança e integração B2B (15 min)**

Considere que a MercaFácil usa APIs de parceiros externos:
- Gateway de pagamento externo (PagFácil).
- Transportadora externa (LogExpress).

Responda:
1. Como garantir que as mensagens trocadas com esses parceiros sejam autênticas e integras? (Use os conceitos de WS-Security do cap. 9.)
2. O serviço de logística da LogExpress usa SOAP com autenticação em cabeçalho. Como a MercaFácil integraria esse serviço? Que informações a WSDL da LogExpress precisaria conter?
3. Se a MercaFácil quisesse disponibilizar seus serviços no UDDI para parceiros, quais estruturas de dados precisaria publicar?

### Entregáveis Esperados

1. **Tabela de serviços** com operações e padrões (Fase 1).
2. **Diagrama de arquitetura** (Fase 2) — digitalizado ou fotografado.
3. **Descrição da coreografia** (Fase 3), incluindo tratamento de falhas.
4. **Respostas às perguntas de segurança** (Fase 4).
5. **Apresentação de 5 minutos** para a turma, destacando as principais decisões de projeto e trade-offs.

### Extensão Opcional — Desafio Avançado

Implemente o serviço de **Catálogo de Produtos** como uma API REST real (usando Flask/Python ou Spring Boot/Java), com os endpoints:
- `GET /produtos` — lista todos os produtos.
- `GET /produtos/{id}` — detalhes de um produto.
- `PUT /produtos/{id}/estoque` — atualiza quantidade em estoque.

Depois, simule a integração com o serviço de **Carrinho** consumindo essa API. Documente as decisões de projeto: por que REST e não SOAP neste caso?
