CREATE TYPE sentiment AS(
    neg real,
    neu real,
    pos real,
    compound real
)

DROP TABLE global_info

CREATE TABLE global_info(
    target_country TEXT,
    on_day TEXT,
    headline_national TEXT[],
    headline_inter TEXT[],
    on_subject TEXT,
    sentiment_national sentiment[],
    sentiment_inter sentiment[],
    objectivity_national REAL,
    objectivity_inter REAL,
    latest_processed TEXT,
    PRIMARY KEY(target_country,on_subject,on_day)
)

SELECT * FROM global_info

INSERT INTO global_info(
    target_country,
    on_day,
    nation_headline,
    inter_headline,
    on_subject,
    sentiment,
    objectivity,
    latest_processed )
VALUES (
    'Test',
    '2021',
    ARRAY ['test','test2'],
    ARRAY ['test','test2'],
    'econmoy',
    ARRAY[ROW(0.5,0.5,0.5,0.5)::sentiment,ROW(0.5,0.5,0.5,0.5)::sentiment],
    0.5,
    'NOW'
)

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