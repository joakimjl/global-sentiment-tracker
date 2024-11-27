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
WHERE on_day = '20240901'),

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
FROM day_info)

SELECT 
    SUM((vader_res).negative) AS vader_negative,
    SUM((vader_res).neutral) AS vader_neutral,
    SUM((vader_res).positive) AS vader_positive,
    SUM((rober_res).negative) AS rober_negative,
    SUM((rober_res).neutral) AS rober_neutral,
    SUM((rober_res).positive) AS rober_positive
FROM (
    SELECT senti_count_func(vader_compound) AS vader_res,
    senti_count_func(roberto_polarity) AS rober_res
    FROM total_sentiment
) AS subquery;

--Probably overengineered, could be simpler but is fast atleast
CREATE OR REPLACE function senti_count_func(input label_senti) returns count_sentiment as $$

DECLARE 
    negative_count INTEGER := 0;
    neutral_count INTEGER := 0;
    positive_count INTEGER := 0;

BEGIN
    CASE
        WHEN input = 'negative' THEN negative_count := negative_count + 1;
        WHEN input = 'positive' THEN positive_count := positive_count + 1;
    ELSE neutral_count := neutral_count + 1;
    END CASE;
RETURN(ROW(negative_count,neutral_count,positive_count)::count_sentiment);
END;
$$ language plpgsql;

/*
BEGIN
    WHILE i <= 3 LOOP
        name_col := 'count_seti_';
        i := i+1;
        temp_num := CAST(i AS TEXT);
        name_col := CONCAT(name_col, temp_num);
        raise notice 'Name % %', input, res;

    END LOOP;
    RETURN res;
END;
$$ language plpgsql;*/





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