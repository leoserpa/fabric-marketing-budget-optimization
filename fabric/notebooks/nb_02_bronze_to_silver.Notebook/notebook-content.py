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

# # Marketing Analytics | Bronze to Silver
# 
# ### Preparação e transformação dos dados de campanhas digitais
# 
# **Projeto:** Marketing Budget Optimization  
# **Plataforma:** Microsoft Fabric  
# **Arquitetura:** Medallion | Bronze → Silver  
# **Tecnologia:** PySpark  
# **Notebook:** `nb_02_bronze_to_silver`
# 
# ### Objetivo
# 
# Transformar os dados brutos da camada Bronze em uma estrutura confiável e padronizada na camada Silver, aplicando regras de qualidade, tipagem e preparação dos dados para as etapas analíticas posteriores.
# 
# **Principais etapas:**
# 
# - Leitura dos dados da camada Bronze
# - Padronização e tipagem das variáveis
# - Aplicação das regras de qualidade
# - Preparação das métricas de marketing
# - Criação da tabela Silver
# - Validação dos dados transformados

# MARKDOWN ********************

# # 0. Instalando e Importando Bibliotecas Necessárias

# CELL ********************

# Imports

from pyspark.sql import functions as F
from pyspark.sql import types as T

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 1. Leitura da Camada Bronze

# CELL ********************

# Leitura dos dados brutos

file_path = "Files/bronze/raw/tech_advertising_campaigns_dataset.csv"

df_bronze = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(file_path)
)

display(df_bronze.limit(10))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 2. Preparação da Camada Silver

# CELL ********************

# Padronização dos tipos de dados

df_silver = (
    df_bronze
    .withColumn("campaign_id", F.col("campaign_id").cast(T.StringType()))
    .withColumn("start_date", F.col("start_date").cast(T.DateType()))
    .withColumn("quarter", F.col("quarter").cast(T.IntegerType()))
    .withColumn("hour_of_day", F.col("hour_of_day").cast(T.IntegerType()))
    .withColumn("campaign_day", F.col("campaign_day").cast(T.IntegerType()))
    .withColumn("quality_score", F.col("quality_score").cast(T.IntegerType()))
    .withColumn("impressions", F.col("impressions").cast(T.LongType()))
    .withColumn("clicks", F.col("clicks").cast(T.LongType()))
    .withColumn("conversions", F.col("conversions").cast(T.LongType()))
    .withColumn("ad_spend", F.col("ad_spend").cast(T.DoubleType()))
    .withColumn("revenue", F.col("revenue").cast(T.DoubleType()))
)

df_silver.printSchema()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Recalculo das metricas de marketing

df_silver = (
    df_silver
    .withColumn(
        "CTR",
        F.when(
            F.col("impressions") > 0,
            (F.col("clicks") / F.col("impressions")) * 100
        ).otherwise(0.0)
    )
    .withColumn(
        "CPC",
        F.when(
            F.col("clicks") > 0,
            F.col("ad_spend") / F.col("clicks")
        ).otherwise(0.0)
    )
    .withColumn(
        "conversion_rate",
        F.when(
            F.col("clicks") > 0,
            (F.col("conversions") / F.col("clicks")) * 100
        ).otherwise(0.0)
    )
    .withColumn(
        "CPA",
        F.when(
            F.col("conversions") > 0,
            F.col("ad_spend") / F.col("conversions")
        ).otherwise(0.0)
    )
    .withColumn(
        "ROAS",
        F.when(
            F.col("ad_spend") > 0,
            F.col("revenue") / F.col("ad_spend")
        ).otherwise(0.0)
    )
    .withColumn(
        "profit",
        F.col("revenue") - F.col("ad_spend")
    )
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Visualizacao das metricas recalculadas

display(
    df_silver.select(
        "campaign_id",
        "impressions",
        "clicks",
        "conversions",
        "ad_spend",
        "revenue",
        "CTR",
        "CPC",
        "conversion_rate",
        "CPA",
        "ROAS",
        "profit"
    ).limit(10)
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 3. Aplicação das Regras de Qualidade

# CELL ********************

# Identificacao de registros que violam as regras de qualidade

df_invalidos = df_silver.filter(
    (F.col("campaign_id").isNull()) |
    (F.col("impressions") < 0) |
    (F.col("clicks") < 0) |
    (F.col("conversions") < 0) |
    (F.col("ad_spend") < 0) |
    (F.col("revenue") < 0) |
    (F.col("clicks") > F.col("impressions")) |
    (F.col("conversions") > F.col("clicks"))
)

quantidade_invalidos = df_invalidos.count()

print(f"Registros inválidos: {quantidade_invalidos:,}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 4. Gravação da Camada Silver

# CELL ********************

# Preparação dos dados válidos para a camada Silver

df_silver_final = df_silver.filter(
    (F.col("campaign_id").isNotNull()) &
    (F.col("impressions") >= 0) &
    (F.col("clicks") >= 0) &
    (F.col("conversions") >= 0) &
    (F.col("ad_spend") >= 0) &
    (F.col("revenue") >= 0) &
    (F.col("clicks") <= F.col("impressions")) &
    (F.col("conversions") <= F.col("clicks"))
)

print(f"Registros preparados para a Silver: {df_silver_final.count():,}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Gravação da tabela Silver no Lakehouse

tabela_silver = "silver_marketing_campaigns"

(
    df_silver_final.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(tabela_silver)
)

print(f"Tabela '{tabela_silver}' criada com sucesso.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 5. Validação da Camada Silver

# CELL ********************

# Leitura e validação da tabela Silver

df_validacao_silver = spark.table("silver_marketing_campaigns")

total_registros = df_validacao_silver.count()
total_colunas = len(df_validacao_silver.columns)

print(f"Registros na Silver: {total_registros:,}")
print(f"Colunas na Silver: {total_colunas}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Comparação entre as camadas Bronze e Silver

registros_bronze = df_bronze.count()
registros_silver = df_validacao_silver.count()

ids_bronze = df_bronze.select("campaign_id").distinct().count()
ids_silver = df_validacao_silver.select("campaign_id").distinct().count()

print(f"Registros na Bronze: {registros_bronze:,}")
print(f"Registros na Silver: {registros_silver:,}")
print(f"IDs únicos na Bronze: {ids_bronze:,}")
print(f"IDs únicos na Silver: {ids_silver:,}")
print(f"Registros perdidos: {registros_bronze - registros_silver:,}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 6. Conclusões
# 
# A transformação da camada Bronze para a camada Silver foi concluída com sucesso.
# 
# Os dados brutos foram lidos a partir do Lakehouse, tiveram seus principais tipos de dados padronizados e as métricas de marketing foram recalculadas a partir das variáveis de origem.
# 
# As regras de qualidade não identificaram registros inválidos. A comparação entre as camadas Bronze e Silver confirmou a preservação dos 10.000 registros e dos 10.000 identificadores únicos de campanha, sem perda ou duplicação de dados durante o processo.
# 
# A tabela `silver_marketing_campaigns` foi armazenada em formato Delta no Lakehouse e está preparada para servir como fonte confiável para as próximas etapas de modelagem e análise.
