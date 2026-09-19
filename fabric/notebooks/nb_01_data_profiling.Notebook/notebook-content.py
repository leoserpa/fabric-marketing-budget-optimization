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

# # Marketing Analytics | Data Profiling
# 
# ### Análise de qualidade e consistência dos dados de campanhas digitais
# 
# **Projeto:** Marketing Budget Optimization  
# **Plataforma:** Microsoft Fabric  
# **Arquitetura:** Medallion | Camada Bronze  
# **Tecnologia:** PySpark  
# **Notebook:** `nb_01_data_profiling`
# 
# ### Objetivo
# 
# Realizar o profiling dos dados brutos de campanhas digitais, avaliando sua estrutura, qualidade e consistência antes do processo de transformação para a camada Silver.
# 
# **Principais análises:**
# 
# - Estrutura e tipos dos dados
# - Valores nulos e registros duplicados
# - Cardinalidade e variáveis categóricas
# - Estatísticas descritivas
# - Regras de negócio
# - Validação de métricas de marketing
# - Identificação e análise de potenciais outliers

# MARKDOWN ********************

# # 0. Instalando e Importando Bibliotecas Necessárias

# CELL ********************

# IMPORTS
from pyspark.sql import functions as F

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 1. Visão Geral dos Dados

# CELL ********************

# Camada Bronze - Leitura dos dados brutos

file_path = "Files/bronze/raw/tech_advertising_campaigns_dataset.csv"

df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(file_path)
)

display(df.limit(20))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Dimensões do conjunto de dados

row_count = df.count()
column_count = len(df.columns)

print(f"Quantidade de linhas: {row_count:,}")
print(f"Quantidade de colunas: {column_count}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Schema inferido pelo Spark

df.printSchema()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 2. Qualidade dos Dados

# CELL ********************

# Análise de valores nulos

null_profile = df.select([
    F.sum(F.col(c).isNull().cast("int")).alias(c)
    for c in df.columns
])

display(null_profile)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Verificação de registros duplicados

total_registros = df.count()
registros_distintos = df.distinct().count()
registros_duplicados = total_registros - registros_distintos

print(f"Total de registros: {total_registros:,}")
print(f"Registros distintos: {registros_distintos:,}")
print(f"Registros duplicados: {registros_duplicados:,}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Verificação de unicidade do ID da campanha

ids_campanha_unicos = df.select("campaign_id").distinct().count()
total_registros = df.count()

print(f"IDs de campanha únicos: {ids_campanha_unicos:,}")
print(f"Total de registros: {total_registros:,}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 3. Análise das Variáveis

# CELL ********************

# Análise de cardinalidade das colunas

cardinalidade = []

for coluna in df.columns:
    valores_distintos = df.select(coluna).distinct().count()
    cardinalidade.append((coluna, valores_distintos))

df_cardinalidade = spark.createDataFrame(
    cardinalidade,
    ["coluna", "valores_distintos"]
).orderBy("valores_distintos")

display(df_cardinalidade)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Análise dos valores das variáveis categóricas

colunas_categoricas = [
    "campaign_objective",
    "platform",
    "ad_placement",
    "device_type",
    "operating_system",
    "creative_format",
    "creative_size",
    "ad_copy_length",
    "creative_emotion",
    "target_audience_age",
    "target_audience_gender",
    "audience_interest_category",
    "income_bracket",
    "purchase_intent_score",
    "industry_vertical",
    "budget_tier"
]

for coluna in colunas_categoricas:
    print(f"\n{coluna}:")
    df.groupBy(coluna).count().orderBy(coluna).show(truncate=False)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Estatísticas descritivas das variáveis numéricas

colunas_numericas = [
    "creative_age_days",
    "quality_score",
    "actual_cpc",
    "impressions",
    "clicks",
    "conversions",
    "ad_spend",
    "revenue",
    "bounce_rate",
    "avg_session_duration_seconds",
    "pages_per_session",
    "CTR",
    "CPC",
    "conversion_rate",
    "CPA",
    "ROAS",
    "profit"
]

display(
    df.select(colunas_numericas).summary(
        "count",
        "min",
        "25%",
        "50%",
        "75%",
        "max",
        "mean",
        "stddev"
    )
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 4. Validação e Consistência dos Dados

# CELL ********************

# Validação das regras de negócio

validacoes = df.select(
    F.sum((F.col("impressions") < 0).cast("int")).alias("impressoes_negativas"),
    F.sum((F.col("clicks") < 0).cast("int")).alias("cliques_negativos"),
    F.sum((F.col("conversions") < 0).cast("int")).alias("conversoes_negativas"),
    F.sum((F.col("ad_spend") < 0).cast("int")).alias("gastos_negativos"),
    F.sum((F.col("revenue") < 0).cast("int")).alias("receitas_negativas"),
    F.sum((F.col("clicks") > F.col("impressions")).cast("int")).alias("cliques_maiores_impressoes"),
    F.sum((F.col("conversions") > F.col("clicks")).cast("int")).alias("conversoes_maiores_cliques")
)

display(validacoes)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Validação das métricas calculadas

df_validacao_metricas = (
    df
    .withColumn(
        "CTR_calculado",
        F.when(F.col("impressions") > 0,
               F.col("clicks") / F.col("impressions"))
    )
    .withColumn(
        "CPC_calculado",
        F.when(F.col("clicks") > 0,
               F.col("ad_spend") / F.col("clicks"))
    )
    .withColumn(
        "conversion_rate_calculado",
        F.when(F.col("clicks") > 0,
               F.col("conversions") / F.col("clicks"))
    )
    .withColumn(
        "CPA_calculado",
        F.when(F.col("conversions") > 0,
               F.col("ad_spend") / F.col("conversions"))
    )
    .withColumn(
        "ROAS_calculado",
        F.when(F.col("ad_spend") > 0,
               F.col("revenue") / F.col("ad_spend"))
    )
    .withColumn(
        "profit_calculado",
        F.col("revenue") - F.col("ad_spend")
    )
)

display(
    df_validacao_metricas.select(
        "CTR", "CTR_calculado",
        "CPC", "CPC_calculado",
        "conversion_rate", "conversion_rate_calculado",
        "CPA", "CPA_calculado",
        "ROAS", "ROAS_calculado",
        "profit", "profit_calculado"
    ).limit(20)
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Validação das métricas calculadas em todo o conjunto de dados

df_metricas = (
    df
    .withColumn(
        "CTR_calculado",
        F.when(
            F.col("impressions") > 0,
            (F.col("clicks") / F.col("impressions")) * 100
        )
    )
    .withColumn(
        "CPC_calculado",
        F.when(
            F.col("clicks") > 0,
            F.col("ad_spend") / F.col("clicks")
        )
    )
    .withColumn(
        "conversion_rate_calculado",
        F.when(
            F.col("clicks") > 0,
            (F.col("conversions") / F.col("clicks")) * 100
        )
    )
    .withColumn(
        "CPA_calculado",
        F.when(
            F.col("conversions") > 0,
            F.col("ad_spend") / F.col("conversions")
        ).otherwise(0)
    )
    .withColumn(
        "ROAS_calculado",
        F.when(
            F.col("ad_spend") > 0,
            F.col("revenue") / F.col("ad_spend")
        )
    )
    .withColumn(
        "profit_calculado",
        F.col("revenue") - F.col("ad_spend")
    )
)

validacao_metricas = df_metricas.select(
    F.sum((F.abs(F.col("CTR") - F.col("CTR_calculado")) > 0.001).cast("int"))
        .alias("divergencias_CTR"),

    F.sum((F.abs(F.col("CPC") - F.col("CPC_calculado")) > 0.01).cast("int"))
        .alias("divergencias_CPC"),

    F.sum((F.abs(F.col("conversion_rate") - F.col("conversion_rate_calculado")) > 0.001).cast("int"))
        .alias("divergencias_conversion_rate"),

    F.sum((F.abs(F.col("CPA") - F.col("CPA_calculado")) > 0.01).cast("int"))
        .alias("divergencias_CPA"),

    F.sum((F.abs(F.col("ROAS") - F.col("ROAS_calculado")) > 0.01).cast("int"))
        .alias("divergencias_ROAS"),

    F.sum((F.abs(F.col("profit") - F.col("profit_calculado")) > 0.01).cast("int"))
        .alias("divergencias_profit")
)

display(validacao_metricas)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Identificação de potenciais outliers pelo método IQR

colunas_outliers = [
    "impressions",
    "clicks",
    "conversions",
    "ad_spend",
    "revenue",
    "CPA",
    "ROAS",
    "profit"
]

resultado_outliers = []

for coluna in colunas_outliers:
    q1, q3 = df.approxQuantile(coluna, [0.25, 0.75], 0.01)

    iqr = q3 - q1
    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr

    quantidade_outliers = df.filter(
        (F.col(coluna) < limite_inferior) |
        (F.col(coluna) > limite_superior)
    ).count()

    resultado_outliers.append(
        (
            coluna,
            round(q1, 2),
            round(q3, 2),
            round(limite_inferior, 2),
            round(limite_superior, 2),
            quantidade_outliers
        )
    )

df_outliers = spark.createDataFrame(
    resultado_outliers,
    [
        "coluna",
        "Q1",
        "Q3",
        "limite_inferior",
        "limite_superior",
        "quantidade_outliers"
    ]
)

display(df_outliers)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Inspeção dos valores extremos das principais métricas

metricas_extremas = [
    "ROAS",
    "CPA",
    "revenue",
    "profit"
]

for metrica in metricas_extremas:
    print(f"\nMaiores valores de {metrica}:")

    df.select(
        "campaign_id",
        "platform",
        "campaign_objective",
        "impressions",
        "clicks",
        "conversions",
        "ad_spend",
        "revenue",
        "CPA",
        "ROAS",
        "profit"
    ).orderBy(
        F.col(metrica).desc()
    ).show(10, truncate=False)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 5. Conclusões do Profiling

# MARKDOWN ********************

# O conjunto de dados apresentou boa qualidade geral, com 10.000 registros e 41 variáveis. Não foram identificados valores nulos, registros duplicados ou inconsistências na unicidade do identificador das campanhas.
# 
# As variáveis categóricas apresentaram domínios consistentes, sem evidências de duplicidades causadas por diferenças de grafia ou capitalização. A variável `purchase_intent_score`, apesar da nomenclatura, representa uma variável categórica ordinal composta pelos níveis Low, Medium e High.
# 
# As validações das regras de negócio não identificaram valores negativos para impressões, cliques, conversões, gastos ou receitas, nem inconsistências no funil, como quantidade de cliques superior às impressões ou conversões superiores aos cliques.
# 
# As métricas derivadas CTR, CPC, taxa de conversão, CPA, ROAS e lucro foram recalculadas a partir das variáveis brutas e comparadas com os valores fornecidos pelo conjunto de dados. Considerando as respectivas escalas e tolerâncias de arredondamento, não foram encontradas divergências.
# 
# A análise pelo método IQR identificou valores extremos em diversas métricas. Entretanto, a inspeção das campanhas correspondentes demonstrou que esses valores são compatíveis com as relações entre investimento, receita, conversões e volume das campanhas. Dessa forma, os potenciais outliers serão preservados e não serão removidos exclusivamente com base no critério estatístico do IQR.
# 
# Com base no profiling realizado, o conjunto de dados apresenta consistência suficiente para avançar para a etapa de transformação da camada Bronze para a camada Silver.

