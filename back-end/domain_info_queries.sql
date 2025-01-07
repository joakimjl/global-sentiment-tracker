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

SELECT * FROM domain_info

SELECT di.*
FROM domain_info di,
UNNEST(di.country_mentions) AS cm(country_code, count)
WHERE di.domain_weight > 0.1
  AND cm.count > 150000
GROUP BY di.domain


SELECT di.*
FROM domain_info di,
UNNEST(di.country_mentions) AS cm(country_code, count)
WHERE cm.count > 100000
  AND cm.country_code = 'CN'
  AND di.domain_weight >= 0.5
GROUP BY di.domain


SELECT count(country_code) FROM domain_info