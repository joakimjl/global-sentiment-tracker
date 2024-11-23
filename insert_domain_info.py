import psycopg
import requests
import json
from datetime import datetime, timedelta, date
from settings import POSTGRES_PASSWORD, POSTGRES_USER
from psycopg.types.composite import CompositeInfo, register_composite

def geric_sql_insert(table, columns, values, columns_count=6):
    """Takes in table and query, SQL injection protection only needed if users are allowed to query
    """
    conn = psycopg.Connection.connect(dbname = "postgres",
                            user = POSTGRES_USER,
                            password = POSTGRES_PASSWORD,
                            host = "192.168.1.51",
                            port = "5432")

    val_text = "VALUES("
    for i in range(columns_count):
        if i < columns_count-1:
            val_text += "%s,"
        else:
            val_text += "%s)"

    query = "INSERT INTO " + table + columns + val_text

    cur = conn.cursor()
    cur.execute(query,values)

    conn.commit()
    cur.close()
    conn.close()

def insert_domain_info(values):
    """CREATE TYPE country_mentions AS (
    country_code TEXT,
    count INTEGER
    )

    CREATE TABLE domain_info(
        domain TEXT,
        country_code TEXT,
        country_mentions country_mentions[],
        domain_weight REAL,
        change_date TEXT,
        domain_auth INTEGER,
        PRIMARY KEY (domain)
    )"""
    columns = "(domain,country_code,country_mentions,domain_weight,change_date,domain_auth)"
    geric_sql_insert("domain_info",columns,values, columns_count=6)

def fetch_composite(name) -> CompositeInfo:
    conn = psycopg.Connection.connect(dbname = "postgres",
                            user = POSTGRES_USER,
                            password = POSTGRES_PASSWORD,
                            host = "192.168.1.51",
                            port = "5432")
    
    info = CompositeInfo.fetch(conn, name)
    register_composite(info,conn)

    conn.close()

    return info

if __name__ == "__main__":
    info = fetch_composite("country_mentions")

    cou_men_arr = []
    
    cou_men_arr.append(info.python_type("US",10))
    cou_men_arr.append(info.python_type("SE",5))

    time = str(datetime.today().strftime('%Y%m%d%H%M%S'))

    values = ("test.com","US",cou_men_arr,"0.5",time,50)

    #print(f"{values} with len {len(values)}")

    insert_domain_info(values)