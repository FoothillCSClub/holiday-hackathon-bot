\c holiday_hackathon;

CREATE TABLE IF NOT EXISTS Users(
    user_id BIGINT PRIMARY KEY,
    points INT,
    special_codes TEXT[]
);

CREATE TABLE IF NOT EXISTS Codes(
    code TEXT PRIMARY KEY,
    title TEXT,
    points INT
);
