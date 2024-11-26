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

SELECT * 
FROM global_info
WHERE target_country = 'US'
AND on_day = '20240129'
AND on_subject = 'America housing'



--working unnest query for sentiments
SELECT UNNEST(headline_national) AS headline,
    UNNEST(sentiment_national[1:1]) AS senti,
    UNNEST(sentiment_national[2:2]) AS senti_second
FROM global_info
WHERE target_country = 'US'
AND on_day = '20240129'
AND on_subject = 'America housing'




WITH national AS (
SELECT UNNEST(headline_national) as headline, UNNEST(sentiment_national) AS senti
FROM global_info
WHERE target_country = 'US'
AND on_day = '20240129'
AND on_subject = 'America housing'),

second_model AS(
SELECT senti AS second
FROM national
WHERE headline IS NULL)

SELECT 
headline,
senti as vader
FROM national
WHERE headline IS NOT NULL
JOIN headline ON second






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