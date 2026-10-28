-- 1. Shipment tracking  

CREATE DATABASE shipment_db;
USE shipment_db;

CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE
);

CREATE TABLE carriers (
    carrier_id INT AUTO_INCREMENT PRIMARY KEY,
    carrier_name VARCHAR(100) NOT NULL
);

CREATE TABLE shipments (
    shipment_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    carrier_id INT NOT NULL,
    tracking_number VARCHAR(100) NOT NULL UNIQUE,
    status VARCHAR(30) NOT NULL DEFAULT 'Pending',
    shipped_at DATETIME,
    delivered_at DATETIME,
    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),
    FOREIGN KEY (carrier_id)
        REFERENCES carriers(carrier_id),
    INDEX idx_shipment_customer (customer_id),
    INDEX idx_shipment_status (status)
);

CREATE TABLE shipment_events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    shipment_id INT NOT NULL,
    event_status VARCHAR(50) NOT NULL,
    event_location VARCHAR(150),
    event_time DATETIME NOT NULL,
    FOREIGN KEY (shipment_id)
        REFERENCES shipments(shipment_id),
    INDEX idx_event_shipment_time
        (shipment_id, event_time)
);
