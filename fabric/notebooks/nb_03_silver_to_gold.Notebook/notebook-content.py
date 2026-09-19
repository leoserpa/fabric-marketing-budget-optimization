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
