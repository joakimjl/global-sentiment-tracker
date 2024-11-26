CREATE TYPE sentiment AS(
    neg real,
    neu real,
    pos real,
    compound real
)

CREATE TYPE article AS(
    title TEXT,
    domain TEXT
)

CREATE TABLE global_info(
    target_country TEXT,
    on_day TEXT,
    headline_national article[],
    headline_inter article[],
    on_subject TEXT,
    sentiment_national sentiment[][],
    sentiment_inter sentiment[][],
    latest_processed TEXT,
    PRIMARY KEY(target_country,on_subject,on_day)
)

SELECT * FROM global_info

SELECT target_country, count(target_country) 
FROM global_info
GROUP BY target_country

SELECT target_country, on_subject, on_day, 
array_length(headline_national, 1) AS head_nat, 
array_length(headline_inter, 1) AS head_int
FROM global_info
GROUP BY on_subject,target_country,on_day
ORDER BY target_country

SELECT target_country, on_subject, on_day, 
array_length(headline_national, 1) AS head_nat, 
array_length(headline_inter, 1) AS head_int
FROM global_info
WHERE on_day = '20241119'
GROUP BY on_subject,target_country,on_day
ORDER BY target_country


SELECT on_day, 
array_length(headline_national, 1) AS head_nat, 
array_length(headline_inter, 1) AS head_int
FROM global_info
WHERE on_day = '20241119'
GROUP BY on_subject,target_country,on_day
ORDER BY on_day

SELECT target_country, on_day, count(target_country) 
FROM global_info
WHERE on_day = '20241119'
GROUP BY (target_country, on_day)

SELECT *
FROM global_info
WHERE on_subject = 'Japan crime'