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
    PRIMARY KEY(target_country)
)