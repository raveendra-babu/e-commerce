-- Run this in MySQL after the app has started once (tables get created automatically)
USE shop_db;

INSERT INTO products (name, description, price, image_url, stock) VALUES
('Cotton T-Shirt',    'Soft everyday t-shirt in 100% cotton, regular fit.',       399.00, NULL, 50),
('Steel Water Bottle','1 litre insulated bottle, keeps drinks cold for 12 hours.', 649.00, NULL, 30),
('Wireless Mouse',    'Quiet-click wireless mouse with USB receiver.',            549.00, NULL, 25),
('Notebook Pack',     'Pack of 3 ruled notebooks, 200 pages each.',               299.00, NULL, 80),
('Backpack',          'Water-resistant 25L backpack with laptop sleeve.',        1499.00, NULL, 15),
('Desk Lamp',         'LED desk lamp with three brightness levels.',              899.00, NULL, 20);
-- To use a real picture, set image_url to a link, e.g. UPDATE products SET image_url='https://...' WHERE id=1;
