# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "6eeb5045-95f7-4cd5-a066-275576de1c1d",
# META       "default_lakehouse_name": "lh_marketing_analytics",
# META       "default_lakehouse_workspace_id": "592e1a2c-0a53-4a5c-9e77-24b714d51441",
# META       "known_lakehouses": [
# META         {
# META           "id": "6eeb5045-95f7-4cd5-a066-275576de1c1d"
# META         }
# META       ]
# META     }
# META   }
# META }

# MARKDOWN ********************

# # Marketing Analytics | Silver to Gold
# 
# ### Modelagem analítica para otimização do orçamento de marketing
# 
# **Projeto:** Marketing Budget Optimization  
# **Plataforma:** Microsoft Fabric  
# **Arquitetura:** Medallion | Silver → Gold  
# **Tecnologia:** PySpark  
# **Notebook:** `nb_03_silver_to_gold`
# 
# ### Objetivo
# 
# Transformar os dados confiáveis da camada Silver em estruturas analíticas orientadas ao negócio, permitindo avaliar a eficiência dos investimentos em marketing e identificar oportunidades de otimização do orçamento.
# 
# **Principais etapas:**
# 
# - Leitura da tabela Silver
# - Definição dos principais KPIs de marketing
# - Análise de eficiência por plataforma
# - Análise por características das campanhas
# - Construção das tabelas analíticas da camada Gold
# - Validação dos resultados

# MARKDOWN ********************

# # 0. Instalando e Importando Bibliotecas Necessárias

# CELL ********************

# Imports
from pyspark.sql import functions as F

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 1. Leitura da Camada Silver

# CELL ********************

# Leitura da tabela Silver

df_silver = spark.table("silver_marketing_campaigns")

total_registros = df_silver.count()
total_colunas = len(df_silver.columns)

print(f"Registros carregados: {total_registros:,}")
print(f"Colunas disponíveis: {total_colunas}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Visualização dos dados da camada Silver

display(df_silver.limit(10))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 2. Construção das Tabelas Analíticas

# MARKDOWN ********************

# Nesta etapa, serão construídas tabelas analíticas na camada Gold a partir dos dados consolidados da camada Silver.
# 
# As agregações serão orientadas à análise de desempenho e eficiência dos investimentos em marketing, considerando dimensões como plataforma, objetivo da campanha, dispositivo e formato criativo.
# 
# As métricas derivadas serão recalculadas a partir dos valores agregados, evitando médias simples de indicadores como CTR, CPC, taxa de conversão, CPA e ROAS.

# MARKDOWN ********************

# ## 2.1 Desempenho por Plataforma

# CELL ********************

# Agregação dos principais indicadores por plataforma

gold_platform_performance = (
    df_silver
    .groupBy("platform")
    .agg(
        F.count("campaign_id").alias("total_campaigns"),
        F.sum("impressions").alias("total_impressions"),
        F.sum("clicks").alias("total_clicks"),
        F.sum("conversions").alias("total_conversions"),
        F.sum("ad_spend").alias("total_ad_spend"),
        F.sum("revenue").alias("total_revenue")
    )
    .withColumn(
        "CTR",
        F.when(
            F.col("total_impressions") > 0,
            (F.col("total_clicks") / F.col("total_impressions")) * 100
        ).otherwise(0.0)
    )
    .withColumn(
        "CPC",
        F.when(
            F.col("total_clicks") > 0,
            F.col("total_ad_spend") / F.col("total_clicks")
        ).otherwise(0.0)
    )
    .withColumn(
        "conversion_rate",
        F.when(
            F.col("total_clicks") > 0,
            (F.col("total_conversions") / F.col("total_clicks")) * 100
        ).otherwise(0.0)
    )
    .withColumn(
        "CPA",
        F.when(
            F.col("total_conversions") > 0,
            F.col("total_ad_spend") / F.col("total_conversions")
        ).otherwise(0.0)
    )
    .withColumn(
        "ROAS",
        F.when(
            F.col("total_ad_spend") > 0,
            F.col("total_revenue") / F.col("total_ad_spend")
        ).otherwise(0.0)
    )
    .withColumn(
        "profit",
        F.col("total_revenue") - F.col("total_ad_spend")
    )
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Visualização do desempenho por plataforma

display(
    gold_platform_performance
    .orderBy(F.desc("ROAS"))
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## 2.2 Desempenho por Objetivo da Campanha

# CELL ********************

# Agregação dos principais indicadores por objetivo da campanha

gold_objective_performance = (
    df_silver
    .groupBy("campaign_objective")
    .agg(
        F.count("campaign_id").alias("total_campaigns"),
        F.sum("impressions").alias("total_impressions"),
        F.sum("clicks").alias("total_clicks"),
        F.sum("conversions").alias("total_conversions"),
        F.sum("ad_spend").alias("total_ad_spend"),
        F.sum("revenue").alias("total_revenue")
    )
    .withColumn(
        "CTR",
        F.when(
            F.col("total_impressions") > 0,
            (F.col("total_clicks") / F.col("total_impressions")) * 100
        ).otherwise(0.0)
    )
    .withColumn(
        "CPC",
        F.when(
            F.col("total_clicks") > 0,
            F.col("total_ad_spend") / F.col("total_clicks")
        ).otherwise(0.0)
    )
    .withColumn(
        "conversion_rate",
        F.when(
            F.col("total_clicks") > 0,
            (F.col("total_conversions") / F.col("total_clicks")) * 100
        ).otherwise(0.0)
    )
    .withColumn(
        "CPA",
        F.when(
            F.col("total_conversions") > 0,
            F.col("total_ad_spend") / F.col("total_conversions")
        ).otherwise(0.0)
    )
    .withColumn(
        "ROAS",
        F.when(
            F.col("total_ad_spend") > 0,
            F.col("total_revenue") / F.col("total_ad_spend")
        ).otherwise(0.0)
    )
    .withColumn(
        "profit",
        F.col("total_revenue") - F.col("total_ad_spend")
    )
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Visualização do desempenho por objetivo da campanha

display(
    gold_objective_performance
    .orderBy(F.desc("ROAS"))
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## 2.3 Função para Construção das Agregações Gold

# CELL ********************

# Função para agregação dos principais KPIs de marketing

def criar_agregacao_gold(df, dimensao):
    
    return (
        df
        .groupBy(dimensao)
        .agg(
            F.count("campaign_id").alias("total_campaigns"),
            F.sum("impressions").alias("total_impressions"),
            F.sum("clicks").alias("total_clicks"),
            F.sum("conversions").alias("total_conversions"),
            F.sum("ad_spend").alias("total_ad_spend"),
            F.sum("revenue").alias("total_revenue")
        )
        .withColumn(
            "CTR",
            F.when(
                F.col("total_impressions") > 0,
                (F.col("total_clicks") / F.col("total_impressions")) * 100
            ).otherwise(0.0)
        )
        .withColumn(
            "CPC",
            F.when(
                F.col("total_clicks") > 0,
                F.col("total_ad_spend") / F.col("total_clicks")
            ).otherwise(0.0)
        )
        .withColumn(
            "conversion_rate",
            F.when(
                F.col("total_clicks") > 0,
                (F.col("total_conversions") / F.col("total_clicks")) * 100
            ).otherwise(0.0)
        )
        .withColumn(
            "CPA",
            F.when(
                F.col("total_conversions") > 0,
                F.col("total_ad_spend") / F.col("total_conversions")
            ).otherwise(0.0)
        )
        .withColumn(
            "ROAS",
            F.when(
                F.col("total_ad_spend") > 0,
                F.col("total_revenue") / F.col("total_ad_spend")
            ).otherwise(0.0)
        )
        .withColumn(
            "profit",
            F.col("total_revenue") - F.col("total_ad_spend")
        )
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Construção das demais visões analíticas

gold_device_performance = criar_agregacao_gold(
    df_silver,
    "device_type"
)

gold_creative_performance = criar_agregacao_gold(
    df_silver,
    "creative_format"
)

display(
    gold_device_performance
    .orderBy(F.desc("ROAS"))
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## 2.4 Desempenho por Características da Campanha

# CELL ********************

# Construção das visões analíticas por características da campanha

gold_device_performance = criar_agregacao_gold(
    df_silver,
    "device_type"
)

gold_creative_performance = criar_agregacao_gold(
    df_silver,
    "creative_format"
)

gold_placement_performance = criar_agregacao_gold(
    df_silver,
    "ad_placement"
)

gold_audience_performance = criar_agregacao_gold(
    df_silver,
    "audience_interest_category"
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Validação das agregações criadas

print(f"Dispositivos: {gold_device_performance.count()}")
print(f"Formatos criativos: {gold_creative_performance.count()}")
print(f"Posicionamentos: {gold_placement_performance.count()}")
print(f"Categorias de audiência: {gold_audience_performance.count()}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 3. Gravação da Camada Gold
# 
# As estruturas analíticas construídas serão persistidas como tabelas Delta no Lakehouse, disponibilizando dados agregados e métricas de desempenho para consumo nas etapas de análise e visualização no Power BI.

# CELL ********************

# Tabelas analíticas da camada Gold

tabelas_gold = {
    "gold_platform_performance": gold_platform_performance,
    "gold_objective_performance": gold_objective_performance,
    "gold_device_performance": gold_device_performance,
    "gold_creative_performance": gold_creative_performance,
    "gold_placement_performance": gold_placement_performance,
    "gold_audience_performance": gold_audience_performance
}

# Gravação das tabelas Gold em formato Delta

for nome_tabela, dataframe in tabelas_gold.items():
    (
        dataframe.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(nome_tabela)
    )

    print(f"Tabela '{nome_tabela}' criada com sucesso.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 4. Validação da Camada Gold

# CELL ********************

# Validação das tabelas persistidas na camada Gold

tabelas_gold_validacao = {
    "gold_platform_performance": 6,
    "gold_objective_performance": 5,
    "gold_device_performance": 3,
    "gold_creative_performance": 6,
    "gold_placement_performance": 6,
    "gold_audience_performance": 6
}

for nome_tabela, quantidade_esperada in tabelas_gold_validacao.items():

    df_validacao = spark.table(nome_tabela)
    quantidade_registros = df_validacao.count()

    status = (
        "OK"
        if quantidade_registros == quantidade_esperada
        else "VERIFICAR"
    )

    print(
        f"{nome_tabela}: "
        f"{quantidade_registros} registros | "
        f"Esperado: {quantidade_esperada} | "
        f"Status: {status}"
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 5. Conclusões
# 
# A transformação da camada Silver para a camada Gold foi concluída com sucesso.
# 
# A partir dos dados consolidados da tabela `silver_marketing_campaigns`, foram construídas estruturas analíticas orientadas à avaliação do desempenho e da eficiência dos investimentos em marketing.
# 
# As métricas CTR, CPC, taxa de conversão, CPA, ROAS e lucro foram recalculadas a partir dos valores agregados, evitando o uso de médias simples de indicadores derivados.
# 
# Foram criadas e persistidas em formato Delta as seguintes tabelas analíticas:
# 
# - `gold_platform_performance`
# - `gold_objective_performance`
# - `gold_device_performance`
# - `gold_creative_performance`
# - `gold_placement_performance`
# - `gold_audience_performance`
# 
# A validação final confirmou a cardinalidade esperada de todas as tabelas Gold, indicando que as agregações foram persistidas corretamente no Lakehouse.
# 
# Com a camada Gold concluída, os dados estão preparados para consumo analítico e construção dos indicadores e visualizações no Power BI.

