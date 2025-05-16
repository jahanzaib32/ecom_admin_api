-- Insert Categories
INSERT INTO categories (name) VALUES
('Electronics'),
('Books'),
('Home Goods'),
('Clothing');

-- Insert Products
INSERT INTO products (name, description, price, category_id) VALUES
('Smart Speaker Echo Dot', 'Voice-controlled smart speaker', 49.99, 1),
('Wireless Noise-Cancelling Headphones', 'Premium sound quality', 199.99, 1),
('The Great Gatsby', 'Classic novel by F. Scott Fitzgerald', 12.50, 2),
('Coffee Maker Deluxe', '12-cup programmable coffee maker', 79.00, 3),
('Men\'s Cotton T-Shirt', 'Comfortable and stylish', 25.00, 4),
('Laptop Pro 15-inch', 'High-performance laptop for professionals', 1299.00, 1),
('Gardening Tool Set', '5-piece essential gardening tools', 35.50, 3);

-- Insert Inventory (Product IDs will likely be 1, 2, 3, 4, 5, 6, 7)
INSERT INTO inventory (product_id, quantity, low_stock_threshold) VALUES
(1, 50, 10),
(2, 25, 5),
(3, 100, 20),
(4, 30, 8),
(5, 200, 25),
(6, 15, 5),
(7, 8, 5); -- Low stock example

-- Insert Sales (Simulating sales over different periods)
-- Product 1: Smart Speaker Echo Dot (Price 49.99)
INSERT INTO sales (product_id, quantity_sold, sale_price_at_time_of_sale, sale_date, order_id) VALUES
(1, 2, 49.99, NOW() - INTERVAL 35 DAY, 'ORD001'), -- Last month
(1, 1, 49.99, NOW() - INTERVAL 10 DAY, 'ORD002'), -- This month, last week
(1, 3, 49.99, NOW() - INTERVAL 2 DAY, 'ORD003');  -- This month, this week

-- Product 2: Wireless Headphones (Price 199.99)
INSERT INTO sales (product_id, quantity_sold, sale_price_at_time_of_sale, sale_date, order_id) VALUES
(2, 1, 199.99, NOW() - INTERVAL 65 DAY, 'ORD004'), -- Two months ago
(2, 1, 199.99, NOW() - INTERVAL 5 DAY, 'ORD005');  -- This week

-- Product 3: The Great Gatsby (Price 12.50)
INSERT INTO sales (product_id, quantity_sold, sale_price_at_time_of_sale, sale_date, order_id) VALUES
(3, 10, 12.50, NOW() - INTERVAL 90 DAY, 'ORD006'), -- Last quarter
(3, 5, 12.50, NOW() - INTERVAL 1 DAY, 'ORD007');   -- Yesterday

-- Product 5: Men's Cotton T-Shirt (Price 25.00)
INSERT INTO sales (product_id, quantity_sold, sale_price_at_time_of_sale, sale_date, order_id) VALUES
(5, 4, 25.00, NOW() - INTERVAL 15 DAY, 'ORD008'),
(5, 2, 25.00, NOW() - INTERVAL 1 YEAR, 'ORD009'); -- Last year

INSERT INTO sales (product_id, quantity_sold, sale_price_at_time_of_sale, sale_date, order_id) VALUES
(6, 1, 1299.00, NOW() - INTERVAL 3 DAY, 'ORD010');

INSERT INTO inventory_log (product_id, change_in_quantity, reason) VALUES
(1, -2, 'Sale ORD001'), (1, -1, 'Sale ORD002'), (1, -3, 'Sale ORD003'),
(2, -1, 'Sale ORD004'), (2, -1, 'Sale ORD005'),
(3, -10, 'Sale ORD006'), (3, -5, 'Sale ORD007'),
(5, -4, 'Sale ORD008'), (5, -2, 'Sale ORD009'),
(6, -1, 'Sale ORD010');