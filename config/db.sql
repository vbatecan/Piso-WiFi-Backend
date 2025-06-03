CREATE TABLE IF NOT EXISTS devices
(
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    mac_address    TEXT UNIQUE NOT NULL,
    time_remaining INTEGER  DEFAULT 0,
    last_connected DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active      BOOLEAN  DEFAULT TRUE,
    plan_id INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (plan_id) REFERENCES plans (id)
);

CREATE TABLE coin_transactions
(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    mac_address TEXT    NOT NULL,
    coin_value  INTEGER NOT NULL,
    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mac_address) REFERENCES devices (mac_address)
);

CREATE TABLE plans
(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    description TEXT    NOT NULL,
    price       INTEGER NOT NULL,
    duration    INTEGER NOT NULL -- Duration is in seconds
);

INSERT INTO plans (name, description, price, duration)
VALUES ('Basic', 'Basic plan', 5, 30),