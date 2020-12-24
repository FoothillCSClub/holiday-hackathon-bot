\c holiday_hackathon;

CREATE TABLE IF NOT EXISTS Users(
    id serial PRIMARY KEY,
    user_id BIGINT NOT NULL,
    points INT,
    special_codes TEXT[]
);

CREATE TABLE IF NOT EXISTS Codes(
    code TEXT PRIMARY KEY,
    title TEXT,
    points INT
);
