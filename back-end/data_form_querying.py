import psycopg
import json
from os import walk
import math
from datetime import datetime, timedelta, date
from settings import POSTGRES_PASSWORD, POSTGRES_USER, CONNECT_IP_REMOTE
from psycopg.types.composite import CompositeInfo, register_composite
import time
from country_list import countries, countries_map

def connect():
    connection = psycopg.Connection.connect(dbname = "postgres",
                            user = POSTGRES_USER,
                            password = POSTGRES_PASSWORD,
                            host = CONNECT_IP_REMOTE,
                            port = "5432")

    return connection

def count_query(day, on_subject, conn=None): #str(date.strftime('%Y%m%d'))
    if conn is None:
        conn = connect()

    cur = conn.cursor()
    cur.execute("\
    WITH day_info AS(\
    SELECT UNNEST(headline_national) AS headline,\
        UNNEST(sentiment_national[1:1]) AS senti,\
        UNNEST(sentiment_national[2:2]) AS senti_second\
    FROM global_info\
    WHERE on_day = %s AND on_subject = %s),\
\
    total_sentiment AS (SELECT \
        CASE\
            WHEN (senti).compound <= -0.05 THEN 'negative'\
            WHEN (senti).compound >= 0.05 THEN 'positive'\
            ELSE 'neutral'\
        END::label_senti AS vader_compound,\
        CASE\
            WHEN tanh((senti_second).pos - (senti_second).neg) <= -0.05 THEN 'negative'\
            WHEN tanh((senti_second).pos - (senti_second).neg) >= 0.05 THEN 'positive'\
            ELSE 'neutral'\
        END::label_senti AS roberto_polarity\
    FROM day_info)\
\
    SELECT \
        SUM((vader_res).negative) AS vader_negative,\
        SUM((vader_res).neutral) AS vader_neutral,\
        SUM((vader_res).positive) AS vader_positive,\
        SUM((rober_res).negative) AS rober_negative,\
        SUM((rober_res).neutral) AS rober_neutral,\
        SUM((rober_res).positive) AS rober_positive\
    FROM (\
        SELECT senti_count_func(vader_compound) AS vader_res,\
        senti_count_func(roberto_polarity) AS rober_res\
        FROM total_sentiment\
    ) AS subquery;", (str(day.strftime('%Y%m%d')),on_subject)
    )
    return(cur.fetchall())

    

if __name__ == "__main__":
    start = time.time()
    date = date.today()-timedelta(days=89)

    conn = connect()
    cur = conn.cursor()

    cur.execute("CREATE OR REPLACE AGGREGATE sum(count_sentiment)\
(\
    sfunc = test_sum_state,\
    stype = count_sentiment,\
    initcond = '(0,0,0)'\
);\
\
CREATE OR REPLACE function test_sum_state(\
    state count_sentiment,\
    next count_sentiment\
) RETURNS count_sentiment AS $$\
DECLARE \
    negative_count INTEGER := 0;\
    neutral_count INTEGER := 0;\
    positive_count INTEGER := 0;\
BEGIN\
    negative_count := ($1).negative + ($2).negative;\
    neutral_count := ($1).neutral + ($2).neutral;\
    positive_count := ($1).positive + ($2).positive;\
    RETURN ROW(negative_count, neutral_count, positive_count)::count_sentiment;\
END;\
$$ language plpgsql;\ "
    )
    print("Fin")
"""
    conn = connect()

    for i in range(45):
        for country in countries:
            if country in countries_map:
                country = countries_map[country]
            res = count_query(date, f"{country} housing", conn)
            print(res)

    conn.close()

    print(time.time()-start)
"""