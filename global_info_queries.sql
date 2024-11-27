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


--Query to get average sentiment
/* WITH day_info AS(
SELECT UNNEST(headline_national) AS headline,
    UNNEST(sentiment_national[1:1]) AS senti,
    UNNEST(sentiment_national[2:2]) AS senti_second
FROM global_info)

SELECT avg((senti).neg) AS vader_negative,
    avg((senti).neu) AS vader_neutral,
    avg((senti).pos) AS vader_positive,
    avg((senti).compound) AS vader_compound,
    avg((senti_second).neg) AS roberto_negative,
    avg((senti_second).neu) AS roberto_neutral,
    avg((senti_second).pos) AS roberto_positive,
    tanh(avg((senti_second).neg)-avg((senti_second).pos)) AS roberto_polarity
FROM day_info
 */

CREATE TYPE label_senti AS ENUM(
    'negative',
    'neutral',
    'positive'
)

CREATE TYPE count_sentiment AS(
    negative INTEGER,
    neutral INTEGER,
    positive INTEGER
)

--Count days sentiment.


WITH day_info AS(
SELECT UNNEST(headline_national) AS headline,
    UNNEST(sentiment_national[1:1]) AS senti,
    UNNEST(sentiment_national[2:2]) AS senti_second
FROM global_info
WHERE on_day = '20240904'),

total_sentiment AS (SELECT 
    CASE
        WHEN (senti).compound <= -0.05 THEN 'negative'
        WHEN (senti).compound >= 0.05 THEN 'positive'
        ELSE 'neutral'
    END::label_senti AS vader_compound,
    CASE
        WHEN tanh((senti_second).pos - (senti_second).neg) <= -0.05 THEN 'negative'
        WHEN tanh((senti_second).pos - (senti_second).neg) >= 0.05 THEN 'positive'
        ELSE 'neutral'
    END::label_senti AS roberto_polarity
FROM day_info),


do $$
DECLARE 
    i INTEGER := 0;
    name_col TEXT := 'count_seti_';
    temp_num TEXT;
    final_name_col TEXT;

BEGIN
    WHILE i <= 3 LOOP
        name_col := 'count_seti_';
        i := i+1;
        temp_num := CAST(i AS TEXT);
        name_col := CONCAT(name_col, temp_num);
        raise notice 'Name %', name_col;
        
    END LOOP;
END;
$$;

SELECT * FROM count_seti_1



WITH day_info AS(
SELECT UNNEST(headline_national) AS headline,
    UNNEST(sentiment_national[1:1]) AS senti,
    UNNEST(sentiment_national[2:2]) AS senti_second
FROM global_info
WHERE on_day = '20240904')

SELECT headline,
    (senti).compound AS vader_compound,
    tanh((senti_second).pos - (senti_second).neg) AS roberto_polarity
FROM day_info



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