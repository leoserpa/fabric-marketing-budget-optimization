# Artefatos do Microsoft Fabric

> Documentação técnica dos itens de workspace gerenciados como código através do Fabric Git Integration (DataOps).

[Português](README.md) | [English](README.en.md)

---

## Visão Geral

Este diretório contém a representação declarativa de todos os componentes do **Microsoft Fabric** que sustentam o projeto de Otimização de Orçamento de Marketing. 

Diferente de abordagens tradicionais de BI com arquivos binários opacos, todos os artefatos neste repositório utilizam os formatos abertos do ecossistema Fabric (código PySpark, arquivos de configuração JSON, formato de relatório PBIP e definições tabulares em TMDL), permitindo versionamento contínuo, revisão por pares (pull requests) e auditoria de código.

---

## Estrutura do Workspace

```
fabric/
├── lakehouse/
│   └── lh_marketing_analytics.Lakehouse/         # Lakehouse unificado (OneLake)
│
├── notebooks/
│   ├── nb_01_data_profiling.Notebook/            # Profiling exploratório e validações iniciais
│   ├── nb_02_bronze_to_silver.Notebook/          # Limpeza, tipagem e recálculo de métricas
│   ├── nb_03_silver_to_gold.Notebook/            # Agregações e sumários de performance
│   ├── nb_04_gold_star_schema.Notebook/          # Modelagem dimensional Star Schema
│   └── nb_05_data_quality.Notebook/              # Framework de testes automatizados e Quality Gate
│
├── pipelines/
│   └── pl_ingest_marketing_campaigns.DataPipeline/  # Orquestrador mestre ponta a ponta
│
├── semantic_models/
│   └── sm_marketing_analytics.SemanticModel/     # Modelo semântico DirectLake em TMDL
│
└── reports/
    └── Marketing Analytics | Budget Optimization.Report/  # Relatório analítico Power BI (PBIP)
```

---

## 1. Lakehouse (`lakehouse/`)

O Lakehouse central **`lh_marketing_analytics`** opera sobre o **OneLake** da Microsoft e estrutura os dados no padrão Medallion:

* **Área `Files/` (Armazenamento não gerenciado):**
  * `Files/bronze/raw/`: Destino de ingestão do arquivo fonte `tech_advertising_campaigns_dataset.csv`.
* **Área `Tables/` (Tabelas gerenciadas Delta Lake):**
  * **Camada Silver:** `silver_marketing_campaigns` (dados limpos e tipados com histórico de transações via Delta Log).
  * **Camada Gold:** 7 tabelas agregadas para consultas rápidas (`gold_campaign_performance`, `gold_platform_performance`, `gold_objective_performance`, `gold_device_performance`, `gold_creative_performance`, `gold_placement_performance`, `gold_audience_performance`).
  * **Star Schema:** Tabela de fatos `fact_campaign_performance` e 8 dimensões normalizadas (`dim_date`, `dim_platform`, `dim_device`, `dim_objective`, `dim_creative`, `dim_audience`, `dim_placement`, `dim_industry`).

---

## 2. Notebooks PySpark (`notebooks/`)

Os notebooks contêm os scripts Apache Spark (`notebook-content.py`) responsáveis por todo o processamento de dados:

| Notebook | Camada | Objetivo Técnico | Saída Delta |
|:---|:---|:---|:---|
| **nb_01_data_profiling** | Bronze | Análise exploratória de nulos, cardinalidade, unicidade de IDs e detecção de outliers via IQR. | Relatório de profiling textual |
| **nb_02_bronze_to_silver** | Bronze → Silver | Conversão explícita de tipos (Casting), recálculo seguro de métricas com tratamento de divisão por zero e filtros de integridade do funil. | `silver_marketing_campaigns` |
| **nb_03_silver_to_gold** | Silver → Gold | Construção de agregações analíticas multidimensionais via função PySpark parametrizada. | 7 tabelas agregadas `gold_*` |
| **nb_04_gold_star_schema** | Gold → Dimensional | Geração de chaves substitutas (`monotonically_increasing_id`), desacoplamento de atributos e montagem da tabela fato com FKs. | 1 Fato + 8 Dimensões |
| **nb_05_data_quality** | Governança | Execução de testes automatizados de completude, unicidade e integridade referencial (anti-joins) com decisão de Quality Gate. | Log de auditoria Delta |

---

## 3. Pipeline de Orquestração (`pipelines/`)

O pipeline **`pl_ingest_marketing_campaigns`** gerencia o fluxo de execução sequencial das atividades de engenharia de dados:

```
Run_Data_Profiling (nb_01)
       │ (On Success)
       ▼
Run_Bronze_to_Silver (nb_02)
       │ (On Success)
       ▼
Run_Silver_to_Gold (nb_03)
       │ (On Success)
       ▼
Run_Gold_Star_Schema (nb_04)
```

* **Idempotência:** Todas as etapas utilizam o modo de escrita `.mode("overwrite")`, garantindo que execuções repetidas do pipeline não gerem dados duplicados ou inconsistências.
* **Tolerância a Falhas:** Caso qualquer notebook intermediário falhe, o pipeline é interrompido imediatamente para evitar contaminação das camadas analíticas.

---

## 4. Modelo Semântico DirectLake (`semantic_models/`)

O modelo semântico **`sm_marketing_analytics`** conecta-se diretamente aos arquivos Delta do Lakehouse através do modo **DirectLake**, sem necessidade de importação ou cópia intermediária de dados para o Power BI.

* **Padrão TMDL (Tabular Model Definition Language):** O modelo é completamente legível e versionado como texto na pasta `definition/`:
  * `model.tmdl`: Metadados do modelo e referências de tabelas.
  * `relationships.tmdl`: Declaração dos relacionamentos 1:N entre fato e dimensões.
  * `tables/_Medidas.tmdl`: Central de medidas DAX (28+ métricas organizadas em pastas: Financeiro, Performance, Volume e Formatação).
  * `tables/dim_*.tmdl` e `fact_*.tmdl`: Esquemas de colunas, visibilidade e chaves de ordenação.

---

## 5. Relatório Power BI (`reports/`)

O relatório **`Marketing Analytics | Budget Optimization`** utiliza a estrutura PBIP (Power BI Project format) com o layout serializado em `definition/pages/`:

* **Página 1: Executivo:** Visão macro de investimento, receita, lucro, ROAS e custo de aquisição (CPA) com gráficos de eficiência temporal.
* **Página 2: Campanhas:** Diagnóstico de engajamento, taxa de conversão por criativo, retorno por dispositivo e setor econômico.
* **Página 3: Orçamento:** Matriz de alocação de verba, análise de gap entre investimento e receita e classificação de campanhas em Escalar, Manter ou Reavaliar.

---

## Como Replicar este Workspace no Fabric

1. Em um workspace do Microsoft Fabric com capacidade ativa (F-SKU ou Trial), acesse **Workspace Settings** > **Git Integration**.
2. Conecte o repositório GitHub e selecione a branch principal.
3. O Fabric sincronizará automaticamente todas as pastas deste diretório.
4. Envie o dataset `data/tech_advertising_campaigns_dataset.csv` para a pasta `Files/bronze/raw/` do Lakehouse criado.
5. Execute o pipeline `pl_ingest_marketing_campaigns`.
6. Abra o relatório no navegador para visualizar o dashboard atualizado.

---

[Voltar para o Repositório Principal](../README.md)
