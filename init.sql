CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    ticket_number VARCHAR(50) NOT NULL,
    event_name VARCHAR(255) NOT NULL,
    buyer_name VARCHAR(255) NOT NULL
);
