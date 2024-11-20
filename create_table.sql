CREATE TYPE sentiment AS(
    neg real,
    neu real,
    pos real,
    tot real
)

CREATE TABLE global_info(
    target_country TEXT,
    on_day TEXT,
    nation_headline TEXT[],
    inter_headline TEXT[],
    on_subject TEXT,
    sentiment sentiment,
    objectivity REAL,
    latest_processed TEXT,
    PRIMARY KEY(target_country,on_subject,on_day)
)

SELECT * FROM global_info

DROP TABLE global_info

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
    ROW(0.5,0.5,0.5,0.5)::sentiment,
    0.5,
    'NOW'
)

SELECT target_country, on_subject, on_day, array_length(nation_headline, 1) AS headlines
FROM global_info
GROUP BY on_subject,target_country,on_day
ORDER BY target_country



