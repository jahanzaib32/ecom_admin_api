-- sql/schema.sql

CREATE DATABASE IF NOT EXISTS ecom_admin_db;
USE ecom_admin_db;

-- Categories Table
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products Table
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_product_name (name),
    INDEX idx_product_category (category_id)
);

-- Inventory Table
CREATE TABLE IF NOT EXISTS inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL UNIQUE, -- Each product has one inventory entry
    quantity INT NOT NULL DEFAULT 0,
    low_stock_threshold INT NOT NULL DEFAULT 10,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_inventory_product (product_id)
);

-- Sales Table
CREATE TABLE IF NOT EXISTS sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    quantity_sold INT NOT NULL,
    sale_price_at_time_of_sale DECIMAL(10, 2) NOT NULL, -- Price at the time of sale
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    order_id VARCHAR(255), -- Optional: to group items in a single order
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT, -- Don't delete product if sales exist
    INDEX idx_sales_product (product_id),
    INDEX idx_sales_date (sale_date),
    INDEX idx_sales_order_id (order_id)
);

-- Optional: Inventory Log Table (to track changes over time more explicitly)
CREATE TABLE IF NOT EXISTS inventory_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    change_in_quantity INT NOT NULL, -- e.g., -5 for sale, +20 for restock
    reason VARCHAR(255), -- e.g., "Sale (Order #123)", "Restock", "Manual Adjustment"
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);