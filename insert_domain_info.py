import psycopg
import requests
import json
from os import walk
import math
from datetime import datetime, timedelta, date
from settings import POSTGRES_PASSWORD, POSTGRES_USER
from psycopg.types.composite import CompositeInfo, register_composite

def connect():
    connection = psycopg.Connection.connect(dbname = "postgres",
                            user = POSTGRES_USER,
                            password = POSTGRES_PASSWORD,
                            host = "192.168.1.51",
                            port = "5432")

    return connection

def geric_sql_insert(table, columns, values, columns_count=6, connection=None):
    """Takes in table and query, SQL injection protection only needed if users are allowed to query
    """
    if connection == None:
        connection = psycopg.Connection.connect(dbname = "postgres",
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

    cur = connection.cursor()
    cur.execute(query,values)
    connection.commit()
    cur.close()

def insert_domain_info(values,connection):
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
    geric_sql_insert("domain_info", columns, values, columns_count=6, connection=connection)

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

def domain_consolidate():
    file_temp = open("json_files/cn_cleaned.json","r")

    cn_data = json.load(file_temp)

    file_temp.close()

    path = "siterelevancecsvs/"
    
    f = []
    for (dirpath, dirnames, filenames) in walk(path):
        f.extend(filenames)
        break

    info = fetch_composite("country_mentions")
    data_mapped = {}
    time_str = str(datetime.today().strftime('%Y%m%d%H%M%S'))

    file = open("site_country_mention/bq-results-20241122-230741-1732317007922.json","r")

    bigquery_mentions = json.load(file)

    for mapping in bigquery_mentions:
        if mapping["domain"] in data_mapped:
            data_mapped[mapping["domain"]][2].append(info.python_type(mapping["countrycode"],mapping["cnt"]))
        else:
            data_mapped[mapping["domain"]] = (mapping["domain"],None,[info.python_type(mapping["countrycode"],mapping["cnt"])],0,time_str,None)

    file.close()
    
    for file_name in f:
        with open(path+file_name,'r') as file:
            lines = file.readlines()
            for line in lines:
                data = line.split(",")
                domain = data[1]
                if domain in data_mapped:
                    weight = 1/( math.log(float(data[0])+10) + 1) + 0.68
                    if data_mapped[domain][3] < weight:#If domain rank is higher for this country
                        data_mapped[domain] = (domain,
                                            file_name[19]+file_name[20],#country code
                                            data_mapped[domain][2],
                                            weight,#Rank 1-10000 (10k still high ish)
                                            time_str,
                                            data_mapped[domain][5])
                    else:
                        data_mapped[domain] = (domain,
                                            file_name[19]+file_name[20],#country code
                                            data_mapped[domain][2],
                                            weight,#Rank 1-10000 (10k still high ish)
                                            time_str,
                                            data_mapped[domain][5])

    for ele in cn_data:
        try:
            data_mapped[ele['domain']] = (data_mapped[ele['domain']][0],
                                        data_mapped[ele['domain']][1],
                                        data_mapped[ele['domain']][2],
                                        data_mapped[ele['domain']][3],
                                        data_mapped[ele['domain']][4],
                                        ele['domain_auth'])
        except:
            print(f"{ele['domain']} was not in mapping")

    return data_mapped

if __name__ == "__main__":

    connection = connect()

    completed = []

    all_data = domain_consolidate()
    for key in all_data:
        if not all_data[key][0] in completed:
            insert_domain_info(all_data[key],connection)
            completed.append(all_data[key][0])
        else:
            print(all_data[key])

    connection.commit()
    connection.close()