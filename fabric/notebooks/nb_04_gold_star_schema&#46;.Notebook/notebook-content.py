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

# # Marketing Analytics | Gold Star Schema
# 
# ## Modelagem dimensional para análise de desempenho de marketing
# 
# **Projeto:** Marketing Budget Optimization  
# **Plataforma:** Microsoft Fabric  
# **Arquitetura:** Medallion | Gold → Star Schema  
# **Tecnologia:** PySpark  
# **Notebook:** `nb_04_gold_star_schema`
# 
# ## Objetivo
# 
# Transformar os dados analíticos da camada Gold em um modelo dimensional no formato **Star Schema**, preparado para consumo pelo modelo semântico e pelo Power BI.
# 
# A modelagem separa os eventos e métricas de desempenho das campanhas em uma **tabela fato** e organiza os principais atributos de análise em **tabelas dimensão**, permitindo análises multidimensionais com relacionamentos simples e eficientes.
# 
# **Principais etapas:**
# 
# - Leitura da tabela `gold_campaign_performance`
# - Definição da granularidade da tabela fato
# - Construção das tabelas dimensão
# - Geração de chaves para relacionamento
# - Construção da tabela fato
# - Validação da integridade do modelo dimensional
# - Persistência das tabelas Gold em formato Delta
# - Preparação das estruturas para Direct Lake e Power BI


# MARKDOWN ********************

# # 0. Importação das Bibliotecas

# CELL ********************

# Bibliotecas utilizadas na construção do modelo dimensional

from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.window import Window

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 1. Leitura da Camada Gold

# CELL ********************

# Leitura da tabela Gold utilizada como base para o modelo dimensional

tabela_origem = "gold_campaign_performance"

df_gold = spark.table(tabela_origem)

print(f"Tabela de origem: {tabela_origem}")
print(f"Total de registros: {df_gold.count():,}")
print(f"Total de colunas: {len(df_gold.columns)}")

display(df_gold.limit(10))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 2. Definição da Granularidade

# CELL ********************

# Validação da granularidade da tabela de origem

total_registros = df_gold.count()
campanhas_unicas = df_gold.select("campaign_id").distinct().count()

print(f"Total de registros: {total_registros:,}")
print(f"Campanhas únicas: {campanhas_unicas:,}")

if total_registros == campanhas_unicas:
    print("Granularidade validada: cada registro representa uma campanha única.")
else:
    print("Atenção: existem múltiplos registros para uma mesma campanha.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 3. Construção das Dimensões

# MARKDOWN ********************

# ## 3.1 Dimensão Data

# CELL ********************

# Construção da dimensão de data

dim_date = (
    df_gold
    .select("start_date")
    .distinct()
    .filter(F.col("start_date").isNotNull())
    .withColumn("date_key", F.date_format("start_date", "yyyyMMdd").cast("int"))
    .withColumn("year", F.year("start_date"))
    .withColumn("quarter", F.quarter("start_date"))
    .withColumn("month", F.month("start_date"))
    .withColumn("month_name", F.date_format("start_date", "MMMM"))
    .withColumn("day", F.dayofmonth("start_date"))
    .withColumn("day_of_week", F.date_format("start_date", "EEEE"))
    .select(
        "date_key",
        "start_date",
        "year",
        "quarter",
        "month",
        "month_name",
        "day",
        "day_of_week"
    )
    .orderBy("start_date")
)

print(f"Registros da dimensão Data: {dim_date.count():,}")

display(dim_date.limit(20))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## 3.2 Dimensão Plataforma

# CELL ********************

# Construção da dimensão de plataforma

dim_platform = (
    df_gold
    .select("platform")
    .distinct()
    .filter(F.col("platform").isNotNull())
    .orderBy("platform")
    .withColumn(
        "platform_key",
        F.row_number().over(Window.orderBy("platform"))
    )
    .select(
        "platform_key",
        "platform"
    )
)

print(f"Registros da dimensão Plataforma: {dim_platform.count():,}")

display(dim_platform)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## 3.3 Dimensão Dispositivo

# CELL ********************

# Construção da dimensão de dispositivo

dim_device = (
    df_gold
    .select("device_type", "operating_system")
    .distinct()
    .filter(F.col("device_type").isNotNull())
    .orderBy("device_type", "operating_system")
    .withColumn(
        "device_key",
        F.row_number().over(
            Window.orderBy("device_type", "operating_system")
        )
    )
    .select(
        "device_key",
        "device_type",
        "operating_system"
    )
)

print(f"Registros da dimensão Dispositivo: {dim_device.count():,}")

display(dim_device)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## 3.4 Dimensão Objetivo

# CELL ********************

# Construção da dimensão de objetivo da campanha

dim_objective = (
    df_gold
    .select("campaign_objective")
    .distinct()
    .filter(F.col("campaign_objective").isNotNull())
    .orderBy("campaign_objective")
    .withColumn(
        "objective_key",
        F.row_number().over(Window.orderBy("campaign_objective"))
    )
    .select(
        "objective_key",
        "campaign_objective"
    )
)

print(f"Registros da dimensão Objetivo: {dim_objective.count():,}")

display(dim_objective)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## 3.5 Dimensão Criativo

# CELL ********************

# Construção da dimensão de criativo

dim_creative = (
    df_gold
    .select(
        "creative_format",
        "creative_size",
        "ad_copy_length",
        "has_call_to_action",
        "creative_emotion"
    )
    .distinct()
    .orderBy(
        "creative_format",
        "creative_size",
        "ad_copy_length",
        "has_call_to_action",
        "creative_emotion"
    )
    .withColumn(
        "creative_key",
        F.row_number().over(
            Window.orderBy(
                "creative_format",
                "creative_size",
                "ad_copy_length",
                "has_call_to_action",
                "creative_emotion"
            )
        )
    )
    .select(
        "creative_key",
        "creative_format",
        "creative_size",
        "ad_copy_length",
        "has_call_to_action",
        "creative_emotion"
    )
)

print(f"Registros da dimensão Criativo: {dim_creative.count():,}")

display(dim_creative.limit(20))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## 3.6 Dimensão Audiência

# CELL ********************

# Construção da dimensão de audiência

dim_audience = (
    df_gold
    .select(
        "target_audience_age",
        "target_audience_gender",
        "audience_interest_category",
        "income_bracket",
        "purchase_intent_score",
        "retargeting_flag"
    )
    .distinct()
    .orderBy(
        "target_audience_age",
        "target_audience_gender",
        "audience_interest_category",
        "income_bracket",
        "purchase_intent_score",
        "retargeting_flag"
    )
    .withColumn(
        "audience_key",
        F.row_number().over(
            Window.orderBy(
                "target_audience_age",
                "target_audience_gender",
                "audience_interest_category",
                "income_bracket",
                "purchase_intent_score",
                "retargeting_flag"
            )
        )
    )
    .select(
        "audience_key",
        "target_audience_age",
        "target_audience_gender",
        "audience_interest_category",
        "income_bracket",
        "purchase_intent_score",
        "retargeting_flag"
    )
)

print(f"Registros da dimensão Audiência: {dim_audience.count():,}")

display(dim_audience.limit(20))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## 3.7 Dimensão Posicionamento

# CELL ********************

# Construção da dimensão de posicionamento do anúncio

dim_placement = (
    df_gold
    .select("ad_placement")
    .distinct()
    .filter(F.col("ad_placement").isNotNull())
    .orderBy("ad_placement")
    .withColumn(
        "placement_key",
        F.row_number().over(Window.orderBy("ad_placement"))
    )
    .select(
        "placement_key",
        "ad_placement"
    )
)

print(f"Registros da dimensão Posicionamento: {dim_placement.count():,}")

display(dim_placement)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## 3.8 Dimensão Indústria

# CELL ********************

# Construção da dimensão de indústria

dim_industry = (
    df_gold
    .select("industry_vertical")
    .distinct()
    .filter(F.col("industry_vertical").isNotNull())
    .orderBy("industry_vertical")
    .withColumn(
        "industry_key",
        F.row_number().over(Window.orderBy("industry_vertical"))
    )
    .select(
        "industry_key",
        "industry_vertical"
    )
)

print(f"Registros da dimensão Indústria: {dim_industry.count():,}")

display(dim_industry)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 4. Validação das Dimensões

# CELL ********************

# Resumo das dimensões do Star Schema

dimensoes = {
    "dim_date": dim_date,
    "dim_platform": dim_platform,
    "dim_device": dim_device,
    "dim_objective": dim_objective,
    "dim_creative": dim_creative,
    "dim_audience": dim_audience,
    "dim_placement": dim_placement,
    "dim_industry": dim_industry
}

print("Resumo das Dimensões")
print("-" * 40)

for nome, df in dimensoes.items():
    print(f"{nome}: {df.count():,} registros")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 5. Construção da Tabela Fato

# CELL ********************

# Construção da tabela fato com as chaves das dimensões

fact_campaign_performance = (
    df_gold

    # Dimensão Data
    .join(
        dim_date.select("date_key", "start_date"),
        on="start_date",
        how="left"
    )

    # Dimensão Plataforma
    .join(
        dim_platform,
        on="platform",
        how="left"
    )

    # Dimensão Dispositivo
    .join(
        dim_device,
        on=["device_type", "operating_system"],
        how="left"
    )

    # Dimensão Objetivo
    .join(
        dim_objective,
        on="campaign_objective",
        how="left"
    )

    # Dimensão Criativo
    .join(
        dim_creative,
        on=[
            "creative_format",
            "creative_size",
            "ad_copy_length",
            "has_call_to_action",
            "creative_emotion"
        ],
        how="left"
    )

    # Dimensão Audiência
    .join(
        dim_audience,
        on=[
            "target_audience_age",
            "target_audience_gender",
            "audience_interest_category",
            "income_bracket",
            "purchase_intent_score",
            "retargeting_flag"
        ],
        how="left"
    )

    # Dimensão Posicionamento
    .join(
        dim_placement,
        on="ad_placement",
        how="left"
    )

    # Dimensão Indústria
    .join(
        dim_industry,
        on="industry_vertical",
        how="left"
    )

    # Seleção final da tabela fato
    .select(
        "campaign_id",

        # Foreign Keys
        "date_key",
        "platform_key",
        "device_key",
        "objective_key",
        "creative_key",
        "audience_key",
        "placement_key",
        "industry_key",

        # Atributos da campanha
        "budget_tier",
        "hour_of_day",
        "campaign_day",
        "creative_age_days",

        # Métricas comportamentais
        "quality_score",
        "bounce_rate",
        "avg_session_duration_seconds",
        "pages_per_session",

        # Métricas aditivas
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

print(f"Registros da tabela fato: {fact_campaign_performance.count():,}")
print(f"Colunas da tabela fato: {len(fact_campaign_performance.columns)}")

display(fact_campaign_performance.limit(20))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 6. Validação da Integridade Referencial

# CELL ********************

# Validação das chaves estrangeiras da tabela fato

foreign_keys = [
    "date_key",
    "platform_key",
    "device_key",
    "objective_key",
    "creative_key",
    "audience_key",
    "placement_key",
    "industry_key"
]

print("Validação da Integridade Referencial")
print("-" * 45)

total_problemas = 0

for chave in foreign_keys:
    nulos = fact_campaign_performance.filter(
        F.col(chave).isNull()
    ).count()

    total_problemas += nulos
    print(f"{chave}: {nulos:,} chaves não encontradas")

print("-" * 45)

if total_problemas == 0:
    print("Integridade referencial validada: todas as chaves foram encontradas.")
else:
    print(f"Atenção: {total_problemas:,} problemas de integridade encontrados.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 7. Persistência do Star Schema

# CELL ********************

# Persistência das dimensões e da tabela fato em formato Delta

tabelas_star_schema = {
    "dim_date": dim_date,
    "dim_platform": dim_platform,
    "dim_device": dim_device,
    "dim_objective": dim_objective,
    "dim_creative": dim_creative,
    "dim_audience": dim_audience,
    "dim_placement": dim_placement,
    "dim_industry": dim_industry,
    "fact_campaign_performance": fact_campaign_performance
}

for nome_tabela, dataframe in tabelas_star_schema.items():
    (
        dataframe.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(nome_tabela)
    )

    print(f"{nome_tabela}: persistida com sucesso.")

print("\nStar Schema persistido com sucesso na camada Gold.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 8. Validação Final do Star Schema

# CELL ********************

# Validação final das tabelas persistidas no Lakehouse

tabelas_esperadas = {
    "dim_date": 761,
    "dim_platform": 6,
    "dim_device": 15,
    "dim_objective": 5,
    "dim_creative": 1162,
    "dim_audience": 2064,
    "dim_placement": 6,
    "dim_industry": 6,
    "fact_campaign_performance": 10000
}

print("Validação Final do Star Schema")
print("-" * 55)

validacao_ok = True

for tabela, esperado in tabelas_esperadas.items():
    total = spark.table(tabela).count()
    status = "OK" if total == esperado else "ERRO"

    if total != esperado:
        validacao_ok = False

    print(
        f"{tabela:<30} "
        f"{total:>7,} registros | {status}"
    )

print("-" * 55)

if validacao_ok:
    print("Star Schema validado com sucesso.")
else:
    print("Atenção: foram encontradas divergências no Star Schema.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
