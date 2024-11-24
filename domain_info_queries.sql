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

SELECT di.*
FROM domain_info di,
UNNEST(di.country_mentions) AS cm(country_code, count)
WHERE di.domain_weight > 0.5
  AND cm.count > 1500
GROUP BY di.domain


SELECT di.*
FROM domain_info di,
UNNEST(di.country_mentions) AS cm(country_code, count)
WHERE di.domain_weight > 0.5
  AND cm.count > 100000
  AND cm.country_code = 'CH'
  AND di.domain LIKE '%.cn'
GROUP BY di.domain



SELECT count(country_code) FROM domain_info