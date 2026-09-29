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

# # Marketing Analytics | Data Quality
# 
# ## Validação da qualidade e integridade dos dados analíticos
# 
# **Projeto:** Marketing Budget Optimization  
# **Plataforma:** Microsoft Fabric  
# **Arquitetura:** Medallion | Gold → Data Quality  
# **Tecnologia:** PySpark  
# **Notebook:** `nb_05_data_quality`
# 
# ## Objetivo
# 
# Validar a **qualidade, consistência e integridade dos dados** utilizados no modelo analítico de marketing, garantindo que as tabelas do Star Schema estejam adequadas para consumo pelo modelo semântico e pelo Power BI.
# 
# A validação contempla aspectos de **completude, unicidade, validade, integridade referencial, consistência das métricas e granularidade da tabela fato**.
# 
# **Principais etapas:**
# - Leitura das tabelas do Star Schema
# - Validação da estrutura dos dados
# - Inicialização do framework de testes
# - Validação de valores nulos
# - Validação de duplicidades
# - Validação da integridade referencial
# - Validação das regras de negócio
# - Validação da consistência das métricas
# - Validação da granularidade da tabela fato
# - Consolidação e persistência do log de auditoria
# - Relatório final e Quality Gate


# MARKDOWN ********************

# # 0. Importação das Bibliotecas

# CELL ********************

# Bibliotecas utilizadas na validação da qualidade dos dados

from pyspark.sql import functions as F
from pyspark.sql import types as T
from datetime import datetime

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 1. Leitura das Tabelas do Star Schema

# CELL ********************

# Dicionário centralizado das tabelas do Star Schema

tabelas_star_schema = {
    "dim_date": spark.table("dim_date"),
    "dim_platform": spark.table("dim_platform"),
    "dim_device": spark.table("dim_device"),
    "dim_objective": spark.table("dim_objective"),
    "dim_creative": spark.table("dim_creative"),
    "dim_audience": spark.table("dim_audience"),
    "dim_placement": spark.table("dim_placement"),
    "dim_industry": spark.table("dim_industry"),
    "fact_campaign_performance": spark.table("fact_campaign_performance")
}

# Referências diretas para uso nas validações
fact = tabelas_star_schema["fact_campaign_performance"]

dimensoes = {
    k: v for k, v in tabelas_star_schema.items()
    if k.startswith("dim_")
}

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Validação da volumetria das tabelas

print("Volumetria do Star Schema")
print("-" * 50)

for nome_tabela, df in tabelas_star_schema.items():
    print(
        f"{nome_tabela:<30} "
        f"{df.count():>7,} registros | "
        f"{len(df.columns)} colunas"
    )

print("-" * 50)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 2. Validação da Estrutura dos Dados

# CELL ********************

# Schema da tabela fato

print("===== fact_campaign_performance =====")
fact.printSchema()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Schemas das tabelas dimensionais

for nome_tabela, df in dimensoes.items():
    print(f"\n===== {nome_tabela} =====")
    df.printSchema()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 3. Inicialização do Framework de Testes

# CELL ********************

# Framework de registro de resultados dos testes

resultados_dq = []

data_execucao = datetime.now()

def registrar_resultado(
    test_id,
    categoria,
    tabela,
    regra,
    total,
    falhas,
    severidade="CRITICAL"
):
    status = "PASSED" if falhas == 0 else "FAILED"

    resultados_dq.append({
        "test_id": test_id,
        "categoria": categoria,
        "tabela": tabela,
        "regra": regra,
        "total_registros": int(total),
        "registros_com_falha": int(falhas),
        "status": status,
        "severidade": severidade,
        "data_execucao": data_execucao
    })

    icone = "✅" if status == "PASSED" else "❌"

    print(
        f"{icone} [{status}] {test_id} | "
        f"{tabela} | {regra} "
        f"(Falhas: {falhas:,})"
    )

print(f"Framework inicializado em: {data_execucao}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 4. Validação de Valores Nulos (Completude)
# 
# Verifica se os campos obrigatórios do modelo dimensional estão livres de valores nulos.

# CELL ********************

# Validação de nulos nas chaves primárias das dimensões

print("Validação de Nulos | Chaves Primárias das Dimensões")
print("-" * 60)

for nome_dim, df_dim in dimensoes.items():
    col_pk = [
        c for c in df_dim.columns
        if c.endswith("_key")
    ][0]

    nulos = df_dim.filter(F.col(col_pk).isNull()).count()

    registrar_resultado(
        f"DQ-NUL-{col_pk.upper()}",
        "Completude",
        nome_dim,
        f"Chave primária '{col_pk}' não deve conter nulos",
        df_dim.count(),
        nulos
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Validação de nulos nos campos críticos da tabela fato

print("Validação de Nulos | Campos Críticos da Tabela Fato")
print("-" * 60)

colunas_criticas_fato = [
    "campaign_id",
    "date_key",
    "platform_key",
    "device_key",
    "objective_key",
    "creative_key",
    "audience_key",
    "placement_key",
    "industry_key",
    "impressions",
    "clicks",
    "conversions",
    "ad_spend",
    "revenue"
]

total_fato = fact.count()

for col in colunas_criticas_fato:
    nulos = fact.filter(F.col(col).isNull()).count()

    registrar_resultado(
        f"DQ-NUL-FATO-{col.upper()}",
        "Completude",
        "fact_campaign_performance",
        f"Coluna '{col}' não deve conter nulos",
        total_fato,
        nulos
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 5. Validação de Duplicidades (Unicidade)

# CELL ********************

# Unicidade das chaves primárias nas dimensões

print("Validação de Unicidade | Chaves Primárias das Dimensões")
print("-" * 60)

for nome_dim, df_dim in dimensoes.items():
    col_pk = [
        c for c in df_dim.columns
        if c.endswith("_key")
    ][0]

    total = df_dim.count()
    unicos = df_dim.select(col_pk).distinct().count()
    duplicatas = total - unicos

    registrar_resultado(
        f"DQ-UNQ-{col_pk.upper()}",
        "Unicidade",
        nome_dim,
        f"Chave primária '{col_pk}' deve ser única",
        total,
        duplicatas
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Unicidade do campaign_id na tabela fato

print("Validação de Unicidade | campaign_id na Tabela Fato")
print("-" * 60)

campanhas_unicas = (
    fact.select("campaign_id")
    .distinct()
    .count()
)

registrar_resultado(
    "DQ-UNQ-CAMPAIGN-ID",
    "Unicidade",
    "fact_campaign_performance",
    "Identificador 'campaign_id' deve ser único",
    total_fato,
    total_fato - campanhas_unicas
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 6. Validação da Integridade Referencial
# 
# Verifica se **todas as chaves estrangeiras** da tabela fato possuem correspondência nas respectivas tabelas dimensão.
# 
# Chaves órfãs (presentes na fato mas ausentes na dimensão) causam valores em branco no Power BI e comprometem a confiabilidade das medidas DAX que dependem de filtros por dimensão.
# 
# A técnica utilizada é o **Anti Join**: retorna apenas os registros da fato que **não possuem** correspondência na dimensão.

# CELL ********************

# Integridade referencial via Anti Join

print("Validação de Integridade Referencial | FK → PK")
print("-" * 60)

chaves_referenciais = {
    "dim_date":      "date_key",
    "dim_platform":  "platform_key",
    "dim_device":    "device_key",
    "dim_objective": "objective_key",
    "dim_creative":  "creative_key",
    "dim_audience":  "audience_key",
    "dim_placement": "placement_key",
    "dim_industry":  "industry_key"
}

for dim_nome, fk_col in chaves_referenciais.items():
    dim_df = dimensoes[dim_nome]

    # Anti Join: busca registros na fato sem correspondência na dimensão
    orfaos = (
        fact
        .join(dim_df, on=fk_col, how="left_anti")
        .count()
    )

    registrar_resultado(
        f"DQ-FK-{fk_col.upper()}",
        "Integridade Referencial",
        "fact_campaign_performance",
        f"FK '{fk_col}' deve existir na dimensão '{dim_nome}'",
        total_fato,
        orfaos
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 7. Validação das Regras de Negócio
# 
# Aplica as regras de domínio de marketing digital para garantir que os dados façam sentido do ponto de vista de negócio.
# 
# - Cliques não podem superar impressões
# - Conversões não podem superar cliques
# - Investimento e receita não podem ser negativos
# - Quality score deve estar entre 1 e 10
# - Bounce rate deve estar entre 0 e 100

# CELL ********************

# Regra 1: Cliques não podem superar impressões

print("Validação de Regras de Negócio")
print("-" * 60)

invalidos_cliques = (
    fact
    .filter(F.col("clicks") > F.col("impressions"))
    .count()
)

registrar_resultado(
    "DQ-REG-CLICKS-IMP",
    "Regra de Negócio",
    "fact_campaign_performance",
    "Cliques não podem ser maiores que impressões",
    total_fato,
    invalidos_cliques
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Regra 2: Conversões não podem superar cliques

invalidos_conv = (
    fact
    .filter(F.col("conversions") > F.col("clicks"))
    .count()
)

registrar_resultado(
    "DQ-REG-CONV-CLICKS",
    "Regra de Negócio",
    "fact_campaign_performance",
    "Conversões não podem ser maiores que cliques",
    total_fato,
    invalidos_conv
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Regra 3: Investimento e receita não podem ser negativos

valores_negativos = (
    fact
    .filter(
        (F.col("ad_spend") < 0) |
        (F.col("revenue") < 0)
    )
    .count()
)

registrar_resultado(
    "DQ-REG-FINANCEIRO-POSITIVO",
    "Regra de Negócio",
    "fact_campaign_performance",
    "Investimento e receita não podem ser negativos",
    total_fato,
    valores_negativos
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Regra 4: Quality score deve estar entre 1 e 10

qs_invalidos = (
    fact
    .filter(
        (F.col("quality_score") < 1) |
        (F.col("quality_score") > 10)
    )
    .count()
)

registrar_resultado(
    "DQ-REG-QUALITY-SCORE",
    "Regra de Negócio",
    "fact_campaign_performance",
    "Quality score deve estar entre 1 e 10",
    total_fato,
    qs_invalidos,
    severidade="WARNING"
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Regra 5: Bounce rate deve estar entre 0 e 100

br_invalidos = (
    fact
    .filter(
        (F.col("bounce_rate") < 0) |
        (F.col("bounce_rate") > 100)
    )
    .count()
)

registrar_resultado(
    "DQ-REG-BOUNCE-RATE",
    "Regra de Negócio",
    "fact_campaign_performance",
    "Bounce rate deve estar entre 0 e 100",
    total_fato,
    br_invalidos,
    severidade="WARNING"
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 8. Validação da Consistência das Métricas
# 
# Verifica se as métricas derivadas foram calculadas corretamente a partir das métricas base.

# CELL ********************

# Consistência do lucro (profit = revenue - ad_spend)

print("Validação de Consistência das Métricas")
print("-" * 60)

inconsistencias_lucro = (
    fact
    .filter(
        F.abs(
            F.col("profit") -
            (F.col("revenue") - F.col("ad_spend"))
        ) > 0.01
    )
    .count()
)

registrar_resultado(
    "DQ-MET-PROFIT",
    "Consistência de Métrica",
    "fact_campaign_performance",
    "Lucro deve ser igual a (revenue - ad_spend)",
    total_fato,
    inconsistencias_lucro
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Consistência do ROAS (ROAS = revenue / ad_spend quando ad_spend > 0)

inconsistencias_roas = (
    fact
    .filter(F.col("ad_spend") > 0)
    .filter(
        F.abs(
            F.col("ROAS") -
            (F.col("revenue") / F.col("ad_spend"))
        ) > 0.01
    )
    .count()
)

registrar_resultado(
    "DQ-MET-ROAS",
    "Consistência de Métrica",
    "fact_campaign_performance",
    "ROAS deve ser igual a (revenue / ad_spend)",
    fact.filter(F.col("ad_spend") > 0).count(),
    inconsistencias_roas
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Consistência do CTR (CTR = (clicks / impressions) * 100 quando impressions > 0)

inconsistencias_ctr = (
    fact
    .filter(F.col("impressions") > 0)
    .filter(
        F.abs(
            F.col("CTR") -
            ((F.col("clicks") / F.col("impressions")) * 100)
        ) > 0.01
    )
    .count()
)

registrar_resultado(
    "DQ-MET-CTR",
    "Consistência de Métrica",
    "fact_campaign_performance",
    "CTR deve ser igual a (clicks / impressions) * 100",
    fact.filter(F.col("impressions") > 0).count(),
    inconsistencias_ctr
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Consistência do CPA (CPA = ad_spend / conversions quando conversions > 0)

inconsistencias_cpa = (
    fact
    .filter(F.col("conversions") > 0)
    .filter(
        F.abs(
            F.col("CPA") -
            (F.col("ad_spend") / F.col("conversions"))
        ) > 0.01
    )
    .count()
)

registrar_resultado(
    "DQ-MET-CPA",
    "Consistência de Métrica",
    "fact_campaign_performance",
    "CPA deve ser igual a (ad_spend / conversions)",
    fact.filter(F.col("conversions") > 0).count(),
    inconsistencias_cpa
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 9. Validação da Granularidade da Tabela Fato
# 
# Verifica se o volume da tabela fato está dentro da faixa esperada.
# 
# Uma variação significativa no volume pode indicar falha silenciosa na ingestão, duplicação de registros ou perda de dados durante as transformações.

# CELL ********************

# Validação do volume esperado da tabela fato

print("Validação de Granularidade")
print("-" * 60)

volume_esperado = 10000
divergencia = abs(total_fato - volume_esperado)

registrar_resultado(
    "DQ-GRA-VOLUME-FATO",
    "Granularidade",
    "fact_campaign_performance",
    f"Volume da tabela fato deve ser {volume_esperado:,} registros",
    total_fato,
    divergencia,
    severidade=(
        "WARNING" if divergencia < 100
        else "CRITICAL"
    )
)

print(f"\nVolume esperado: {volume_esperado:,}")
print(f"Volume encontrado: {total_fato:,}")
print(f"Divergência: {divergencia:,}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 10. Consolidação e Persistência do Log de Auditoria
# 
# Converte todos os resultados acumulados em um DataFrame Spark e persiste na tabela Delta `gold_data_quality_audit_log` no Lakehouse.

# CELL ********************

# Conversão dos resultados para DataFrame Spark com tipos seguros

schema_dq = T.StructType([
    T.StructField("test_id", T.StringType(), True),
    T.StructField("categoria", T.StringType(), True),
    T.StructField("tabela", T.StringType(), True),
    T.StructField("regra", T.StringType(), True),
    T.StructField("total_registros", T.LongType(), True),
    T.StructField("registros_com_falha", T.LongType(), True),
    T.StructField("status", T.StringType(), True),
    T.StructField("severidade", T.StringType(), True),
    T.StructField("data_execucao", T.TimestampType(), True)
])

dados_formatados = [
    (
        str(r["test_id"]),
        str(r["categoria"]),
        str(r["tabela"]),
        str(r["regra"]),
        int(r["total_registros"]),
        int(r["registros_com_falha"]),
        str(r["status"]),
        str(r["severidade"]),
        r["data_execucao"]
    )
    for r in resultados_dq
]

df_dq_results = spark.createDataFrame(
    dados_formatados,
    schema=schema_dq
)

display(df_dq_results.orderBy("status", "categoria", "test_id"))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Persistência no Lakehouse como tabela Delta com auto-recuperação

nome_tabela_dq = "gold_data_quality_audit_log"

try:
    # Tenta append se a tabela já existir
    (
        df_dq_results.write
        .format("delta")
        .mode("append")
        .option("mergeSchema", "true")
        .saveAsTable(nome_tabela_dq)
    )
    modo_gravacao = "append"

except Exception:
    # Se falhar (tabela não existe ou está corrompida), limpa e recria
    spark.sql(f"DROP TABLE IF EXISTS {nome_tabela_dq}")

    (
        df_dq_results.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(nome_tabela_dq)
    )
    modo_gravacao = "overwrite (recriada)"

total_historico = spark.table(nome_tabela_dq).count()

print(
    f"✅ Log de qualidade persistido com sucesso (modo: {modo_gravacao}) "
    f"na tabela '{nome_tabela_dq}'."
)
print(
    f"📊 Total de registros no histórico: "
    f"{total_historico:,}"
)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 11. Relatório Final e Quality Gate
# 
# Apresenta o resumo consolidado de todos os testes executados e aplica o **Quality Gate**: se houver qualquer falha com severidade `CRITICAL`, a execução é interrompida com uma exceção para impedir que dados inconsistentes sejam consumidos pelo modelo semântico e pelo Power BI.
# 
# Este mecanismo garante que o Data Pipeline do Fabric só conclua com sucesso quando 100% das regras críticas forem atendidas.

# CELL ********************

# Relatório final e Quality Gate

total_testes = len(resultados_dq)

aprovados = sum(
    1 for r in resultados_dq
    if r["status"] == "PASSED"
)

falhas_criticas = sum(
    1 for r in resultados_dq
    if r["status"] == "FAILED"
    and r["severidade"] == "CRITICAL"
)

falhas_warnings = sum(
    1 for r in resultados_dq
    if r["status"] == "FAILED"
    and r["severidade"] == "WARNING"
)

taxa_sucesso = (aprovados / total_testes) * 100

print("=" * 60)
print("RELATÓRIO FINAL DE QUALIDADE DE DADOS")
print("=" * 60)
print(f"Data da execução:          {data_execucao}")
print(f"Total de testes executados: {total_testes}")
print(f"Testes aprovados (PASSED): {aprovados}")
print(f"Taxa de aprovação:         {taxa_sucesso:.1f}%")
print(f"Falhas críticas (CRITICAL):{falhas_criticas}")
print(f"Alertas (WARNING):         {falhas_warnings}")
print("=" * 60)

if falhas_criticas > 0:
    print("\n❌ QUALITY GATE: REPROVADO")
    raise ValueError(
        f"QUALITY GATE REPROVADO: {falhas_criticas} "
        f"falha(s) crítica(s) identificada(s). "
        f"Pipeline interrompido para proteger "
        f"o modelo semântico e o Power BI."
    )
else:
    print("\n✅ QUALITY GATE: APROVADO")
    print(
        "Todas as regras críticas foram "
        "validadas com 100% de conformidade."
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # 12. Conclusões
# 
# A validação de qualidade dos dados do Star Schema foi concluída.
# 
# Os testes cobriram os seguintes aspectos:
# 
# - **Completude:** Verificação de valores nulos em chaves primárias das dimensões e campos críticos da tabela fato.
# - **Unicidade:** Garantia de que chaves primárias e identificadores são estritamente únicos.
# - **Integridade Referencial:** Confirmação de que todas as chaves estrangeiras da tabela fato possuem correspondência nas dimensões.
# - **Regras de Negócio:** Validação de limites lógicos das métricas de marketing digital.
# - **Consistência de Métricas:** Verificação aritmética de métricas derivadas (lucro, ROAS, CTR, CPA).
# - **Granularidade:** Controle do volume da tabela fato contra o valor esperado.
# 
# Os resultados foram persistidos na tabela Delta `gold_data_quality_audit_log` no Lakehouse, permitindo rastreabilidade histórica e conformidade com auditorias futuras.
# 
# O Quality Gate atua como barreira de proteção: caso alguma regra crítica falhe, o pipeline é interrompido automaticamente, impedindo que dados inconsistentes cheguem ao modelo semântico e ao Power BI.

