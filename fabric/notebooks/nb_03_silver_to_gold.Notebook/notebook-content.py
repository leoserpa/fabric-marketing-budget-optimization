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
# Transformar os dados confiáveis da camada Silver em estruturas analíticas da camada Gold, preparadas para consumo pelo modelo semântico e pelo Power BI.
# 
# A modelagem preserva uma visão detalhada no nível de campanha para análises multidimensionais e também disponibiliza tabelas agregadas para análises específicas de desempenho e eficiência dos investimentos em marketing.
# 
# **Principais etapas:**
# 
# - Leitura da tabela Silver
# - Construção da tabela analítica no nível de campanha
# - Definição dos principais KPIs de marketing
# - Construção de agregações por dimensões de negócio
# - Persistência das tabelas Gold em formato Delta
# - Validação das estruturas analíticas
# - Preparação dos dados para o modelo semântico e Power BI


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

# ## 2.1 Desempenho por Campanha
# 
# Esta tabela preserva a granularidade no nível de campanha e reúne as principais dimensões e métricas necessárias para análises multidimensionais no modelo semântico e no Power BI.
# 
# Diferentemente das tabelas agregadas, essa estrutura permite combinar filtros de plataforma, dispositivo, formato criativo, audiência, objetivo e demais características das campanhas.

# CELL ********************

# Construção da tabela Gold no nível de campanha

gold_campaign_performance = (
    df_silver
    .select(
        # Identificação
        "campaign_id",
        "start_date",
        "quarter",
        "day_of_week",
        "hour_of_day",
        "campaign_day",

        # Estratégia da campanha
        "campaign_objective",
        "platform",
        "ad_placement",
        "device_type",
        "operating_system",
        "industry_vertical",
        "budget_tier",

        # Criativo
        "creative_format",
        "creative_size",
        "ad_copy_length",
        "has_call_to_action",
        "creative_emotion",
        "creative_age_days",

        # Público
        "target_audience_age",
        "target_audience_gender",
        "audience_interest_category",
        "income_bracket",
        "purchase_intent_score",
        "retargeting_flag",

        # Qualidade e comportamento
        "quality_score",
        "bounce_rate",
        "avg_session_duration_seconds",
        "pages_per_session",

        # Métricas base
        "impressions",
        "clicks",
        "conversions",
        "ad_spend",
        "revenue",

        # KPIs
        "CTR",
        "CPC",
        "conversion_rate",
        "CPA",
        "ROAS",
        "profit"
    )
)

display(gold_campaign_performance.limit(20))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Validação da tabela Gold no nível de campanha

total_registros = gold_campaign_performance.count()
total_colunas = len(gold_campaign_performance.columns)
total_campaign_ids = (
    gold_campaign_performance
    .select("campaign_id")
    .distinct()
    .count()
)

print(f"Registros: {total_registros:,}")
print(f"Colunas: {total_colunas}")
print(f"Campaign IDs únicos: {total_campaign_ids:,}")

if total_registros != total_campaign_ids:
    raise ValueError(
        "Foram identificados campaign_id duplicados na tabela Gold."
    )

print("Validação concluída com sucesso.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## 2.2 Desempenho por Plataforma

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

# ## 2.3 Desempenho por Objetivo da Campanha

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

# ## 2.4 Função para Construção das Agregações Gold

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

# ## 2.5 Desempenho por Características da Campanha

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

# Tabelas Gold que serão persistidas no Lakehouse

tabelas_gold = {
    "gold_campaign_performance": gold_campaign_performance,
    "gold_platform_performance": gold_platform_performance,
    "gold_objective_performance": gold_objective_performance,
    "gold_device_performance": gold_device_performance,
    "gold_creative_performance": gold_creative_performance,
    "gold_placement_performance": gold_placement_performance,
    "gold_audience_performance": gold_audience_performance
}

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

validacoes_gold = {
    "gold_campaign_performance": 10000,
    "gold_platform_performance": 6,
    "gold_objective_performance": 5,
    "gold_device_performance": 3,
    "gold_creative_performance": 6,
    "gold_placement_performance": 6,
    "gold_audience_performance": 6
}

for tabela, esperado in validacoes_gold.items():
    
    total = spark.table(tabela).count()
    
    status = "OK" if total == esperado else "VERIFICAR"
    
    print(
        f"{tabela}: {total:,} registros | "
        f"Esperado: {esperado:,} | {status}"
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
# A camada Gold foi estruturada para atender tanto análises multidimensionais no nível de campanha quanto consultas agregadas orientadas a diferentes dimensões de negócio.
# 
# ### Principais resultados
# 
# - Criação da tabela `gold_campaign_performance`, preservando a granularidade de uma linha por campanha
# - Validação de 10.000 campanhas e 10.000 `campaign_id` únicos
# - Construção de tabelas agregadas por plataforma, objetivo, dispositivo, formato criativo, posicionamento e audiência
# - Recálculo dos principais KPIs a partir dos valores consolidados nas tabelas agregadas
# - Persistência de 7 tabelas Gold em formato Delta
# - Validação da quantidade de registros de todas as estruturas analíticas
# 
# A tabela `gold_campaign_performance` será utilizada como principal fonte para o modelo semântico, permitindo análises combinadas entre diferentes características das campanhas e filtros multidimensionais no Power BI.
# 
# As tabelas agregadas complementam a camada Gold com visões específicas de desempenho e eficiência dos investimentos em marketing.
# 
# Com isso, a camada Gold está preparada para consumo analítico e construção do modelo semântico no Power BI.

