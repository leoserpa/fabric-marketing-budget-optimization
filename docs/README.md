# Central de Documentação Técnica

> Portal de referência e guias práticos do projeto **Marketing Budget Optimization** no Microsoft Fabric.

[Português](README.md) | [English](README.en.md)

---

## Visão Geral

Esta pasta reúne toda a documentação detalhada sobre a engenharia de dados, modelagem analítica e regras de negócio do projeto. Se você é um avaliador, engenheiro de dados, analytics engineer ou líder técnico, utilize os guias abaixo para navegar pelos detalhes de implementação.

---

## Índice da Documentação

| Guia | Descrição | Versões |
|:---|:---|:---:|
| [Arquitetura](architecture.md) | Decisões técnicas, Arquitetura Medalhão (Bronze/Silver/Gold), fluxo de dados e diagramas | [PT](architecture.md) \| [EN](architecture.en.md) |
| [Dicionário de Dados](data-dictionary.md) | Especificação das 41 colunas brutas, tabelas Delta Silver/Gold, Star Schema e catálogo de métricas | [PT](data-dictionary.md) \| [EN](data-dictionary.en.md) |
| [Guia dos Notebooks](notebooks-guide.md) | Passo a passo de execução dos notebooks (nb_01 a nb_05), validações, idempotência e Quality Gate | [PT](notebooks-guide.md) \| [EN](notebooks-guide.en.md) |
| [Modelo Semântico & Power BI](semantic-model-guide.md) | Conexão DirectLake, catálogo de 28+ medidas DAX, convenções de código TMDL e regras de cores | [PT](semantic-model-guide.md) \| [EN](semantic-model-guide.en.md) |

---

## Trilha de Leitura Recomendada

Dependendo do seu foco, recomendamos a seguinte ordem de leitura:

### Para Avaliadores Técnicos e Tech Leads
1. [Guia de Arquitetura](architecture.md): Entenda as decisões de design, trade-offs e a topologia Medallion + DirectLake.
2. [Guia do Modelo Semântico](semantic-model-guide.md): Avalie o padrão TMDL, modelagem dimensional e práticas enterprise de DAX.
3. [Guia dos Notebooks](notebooks-guide.md) (Seção nb_05): Conheça o framework automatizado de Data Quality e o Quality Gate.

### Para Engenheiros de Dados e Analytics Engineers
1. [Guia dos Notebooks](notebooks-guide.md): Entenda como o PySpark processa e limpa cada camada dos dados.
2. [Dicionário de Dados](data-dictionary.md): Consulte a tipagem, chaves substitutas (*surrogate keys*) e integridade referencial.
3. [Guia de Arquitetura](architecture.md): Veja como os dados transitam no OneLake e Lakehouse.

---

[Voltar para o Repositório Principal](../README.md)
