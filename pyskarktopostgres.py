import findspark
findspark.init()
from settings import POSTGRES_PASSWORD

from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("PostgreSQL Connection with PySpark") \
    .config("spark.jars", "spark_driver\postgresql-42.7.4.jar") \
    .getOrCreate()

url = "jdbc:postgresql://192.168.1.51:5432/postgres"

properties = {
    "user": "postgres",
    "password": POSTGRES_PASSWORD,
    "driver": "org.postgresql.Driver"
}

table_name = "global_info"

df = spark.read.jdbc(url, table_name, properties=properties)

print()
print(df)
print()