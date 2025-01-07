import findspark
findspark.init()
from settings import POSTGRES_PASSWORD
from GDELT import get_gdelt_processed

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

res = get_gdelt_processed()


"""
target_country: string,
on_day: string,
nation_headline: array<string>,
inter_headline: array<string>,
on_subject: string,
sentiment: string,
objectivity: float,
latest_processed: string
"""
"""
res_df = spark.createDataFrame([
    ("USA","20241120",res[1],["0","0"],"Economy",res[0][0],0.5,"20241120")
])

df.selectExpr(res_df).write.insertInto(table_name)

read_table_res = spark.read.table(table_name).show()

print(read_table_res)
"""