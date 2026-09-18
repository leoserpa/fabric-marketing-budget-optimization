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

# CELL ********************

# Leitura dos dados brutos - Bronze Layer

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

# Dimensões do dataset

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
