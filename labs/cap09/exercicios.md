# Lista de Exercícios — Capítulo 9: Serviços Web

**Disciplina:** Sistemas Distribuídos  
**Referência:** Coulouris et al., *Sistemas Distribuídos*, Cap. 9  
---

## Nível Básico — Conceitual e de Reconhecimento

**Q1.** Defina serviço Web e explique qual é a diferença fundamental entre um *servidor Web* e um *serviço Web*. Use um exemplo concreto para ilustrar.

---

**Q2.** Sobre a arquitetura de infraestrutura dos serviços Web, associe cada componente à sua função:

| Componente   | Função                                                                 |
|--------------|------------------------------------------------------------------------|
| (a) XML      | ( ) Protocolo de empacotamento de mensagens                            |
| (b) SOAP     | ( ) Formato textual auto-descritivo para representação de dados        |
| (c) WSDL     | ( ) Protocolo de transporte de mensagens na Internet                   |
| (d) HTTP     | ( ) Linguagem de descrição de interfaces de serviço                    |
| (e) UDDI     | ( ) Serviço de diretório para publicação e descoberta de serviços Web  |

---

**Q3.** Explique o conceito de **baixo acoplamento** no contexto de serviços Web. Cite dois mecanismos técnicos que contribuem para o baixo acoplamento nesses sistemas.

---

**Q4.** Qual é a estrutura de uma mensagem SOAP? Descreva os dois componentes principais e a função de cada um.

---

**Q5.** Marque V (verdadeiro) ou F (falso) para cada afirmação sobre REST e SOAP:

( ) REST usa operações específicas de negócio definidas em WSDL.  
( ) SOAP pode usar SMTP como protocolo de transporte, além do HTTP.  
( ) No modelo REST, quando um novo recurso é criado, ele recebe um novo URL.  
( ) Segundo Greenfield e Dornan [2004], 80% dos pedidos para os serviços Web da Amazon são feitos via SOAP.  
( ) REST adota uma visão orientada a dados, enquanto o SOAP enfatiza as operações.

---

## Nível Intermediário — Analítico e de Aplicação

**Q6.** Analise o cenário a seguir:

> Uma startup de turismo está desenvolvendo um serviço de agente de viagens que integra automaticamente reservas de voos (fornecedor A e B), hotéis (fornecedor A e B) e aluguel de carro (fornecedor A e B). O serviço deve funcionar com parceiros de qualquer nacionalidade, usando linguagens de programação distintas.

Com base no Capítulo 9, responda:

(a) Quais são os dois padrões de comunicação SOAP que poderiam ser usados nesse cenário? Qual seria mais adequado para a consulta de preços e qual para o pagamento? Justifique.

(b) O serviço de agente de viagens precisará de uma descrição WSDL. Identifique quais seções da WSDL seriam essenciais e o que cada uma descreveria nesse contexto.

(c) Por que o uso de serviços Web é mais adequado do que CORBA nesse cenário de integração entre múltiplas organizações independentes?

---

**Q7.** Compare a segurança baseada em TLS com a segurança em XML (WS-Security). Para cada afirmação abaixo, indique qual abordagem ela descreve:

| Afirmação                                                                 | TLS | XML/WS-Security |
|---------------------------------------------------------------------------|-----|-----------------|
| Protege o canal de comunicação ponto a ponto                              |     |                 |
| Permite cifrar apenas partes selecionadas de um documento                 |     |                 |
| A proteção é uma propriedade do canal, não do documento                   |     |                 |
| O documento pode ser armazenado e repassado mantendo sua proteção         |     |                 |
| Diferentes seções do documento podem ser assinadas por pessoas diferentes |     |                 |

---

**Q8.** Sobre WSDL, responda:

(a) Qual é a diferença entre a **parte abstrata** e a **parte concreta** de uma descrição WSDL?

(b) Explique o papel do elemento **vínculo (binding)** em uma descrição WSDL. Qual a relação entre vínculo e endpoint?

(c) O que é herança de interface em WSDL e qual restrição importante existe sobre ela?

---

**Q9.** O serviço UDDI organiza informações em quatro estruturas de dados principais. Para cada cenário abaixo, identifique qual estrutura seria consultada e por quê:

(a) Uma empresa quer descobrir quais serviços Web de logística estão disponíveis na Internet.

(b) Um desenvolvedor sabe que existe um serviço da empresa "LogEx" e quer obter a URL exata do endpoint para integrar em seu código.

(c) Um novo parceiro precisa entender o contrato formal do serviço (interface, tipos de dados, operações).

---

## Nível Avançado — Síntese, Projeto e Pensamento Crítico

**Q10.** **Projeto de arquitetura:**

Uma universidade pública quer construir uma plataforma de pesquisa científica distribuída, nos moldes do World-Wide Telescope descrito no capítulo. Diferentes laboratórios em países distintos armazenam conjuntos de dados genômicos volumosos (na ordem de terabytes). Pesquisadores de qualquer laboratório devem poder executar análises sobre os dados sem transferi-los para sua máquina local.

Elabore uma proposta arquitetural baseada em serviços Web/SOA para essa plataforma, respondendo:

(a) Quais são os requisitos fundamentais que a plataforma deve atender (baseie-se nos requisitos R1–R6 do Capítulo 9)?

(b) Como os serviços Web satisfazem os dois primeiros requisitos (acesso remoto e processamento local dos dados)?

(c) Qual é o papel do OGSA/Globus nessa arquitetura?

(d) Que considerações de segurança em XML seriam necessárias para garantir que apenas pesquisadores autorizados acessem determinados conjuntos de dados?

---

**Q11.** **Análise crítica — SOA vs. Microsserviços:**

A arquitetura orientada a serviços (SOA) baseada em serviços Web (SOAP/WSDL/UDDI) foi o paradigma dominante no início dos anos 2000. Atualmente, a maioria das novas arquiteturas usa microsserviços com APIs REST e JSON.

(a) Com base no que você estudou sobre serviços Web no Capítulo 9, identifique três vantagens que o modelo SOAP/WSDL oferece sobre REST simples em cenários empresariais complexos.

(b) Identifique dois pontos de crítica ao modelo SOAP/WSDL/UDDI que podem explicar por que ele perdeu espaço para REST/JSON.

(c) O conceito de **coreografia** de serviços Web (Seção 9.6) é mais próximo de qual estilo de orquestração em microsserviços modernos: orquestração centralizada (ex: um coordenador controla o fluxo) ou coreografia descentralizada (ex: eventos e reações)? Justifique.

---

**Q12.** **Estudo de caso — Amazon Web Services:**

O EC2 da Amazon oferece instâncias virtuais elásticas com endereço IP elástico.

(a) O que significa o termo "elástico" no contexto do EC2? Qual problema de sistemas distribuídos ele resolve?

(b) O endereço IP elástico é associado à conta do usuário, não à instância. Qual é o benefício disso em termos de tolerância a falhas?

(c) Relacione o conceito de "computação em nuvem" com a infraestrutura de serviços Web estudada no capítulo. Por que serviços Web são uma implementação natural para computação em nuvem?

(d) Considerando o contexto de Sistemas de Informação, cite um cenário empresarial real em que uma empresa de médio porte poderia se beneficiar de usar AWS EC2 + S3 em vez de manter servidores próprios. Avalie os trade-offs.
