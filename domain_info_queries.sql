CREATE TYPE country_mentions AS (
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
)

DROP TABLE domain_info

SELECT * FROM domain_info

SELECT count(domain) 
FROM domain_info
WHERE domain_weight != 0