-- Business database seed (run against business_db)
-- customer.user_id values must match auth_db user IDs.

----------------------------------------------------
-- CUSTOMERS
----------------------------------------------------

INSERT INTO customers (user_id, first_name, last_name, email, phone)
SELECT
    ('00000000-0000-4000-8000-' || lpad(i::text, 12, '0'))::uuid,
    'CustomerFirst' || i,
    'CustomerLast' || i,
    'user' || i || '@example.com',
    '+9617000' || lpad(i::text, 4, '0')
FROM generate_series(1, 500) i
ON CONFLICT DO NOTHING;

----------------------------------------------------
-- PRODUCTS
----------------------------------------------------

INSERT INTO products (name, description, price, stock, category)
SELECT
    category || ' Product ' || i,
    'Description for product ' || i,
    ROUND((20 + random() * 300)::numeric, 2),
    (random() * 200)::int + 5,
    category
FROM generate_series(1, 1000) i
CROSS JOIN LATERAL (
    SELECT CASE floor(random() * 8)::int
        WHEN 0 THEN 'Shoes'
        WHEN 1 THEN 'Electronics'
        WHEN 2 THEN 'Sports'
        WHEN 3 THEN 'Home'
        WHEN 4 THEN 'Beauty'
        WHEN 5 THEN 'Clothing'
        WHEN 6 THEN 'Accessories'
        ELSE 'Toys'
    END AS category
) c;

----------------------------------------------------
-- ORDERS
----------------------------------------------------

INSERT INTO orders (customer_id, total_price, status, ordered_at)
SELECT
    (random() * 499)::int + 1,
    0,
    CASE floor(random() * 7)::int
        WHEN 0 THEN 'Pending'
        WHEN 1 THEN 'Processing'
        WHEN 2 THEN 'Shipped'
        WHEN 3 THEN 'Delivered'
        WHEN 4 THEN 'Cancelled'
        WHEN 5 THEN 'Refunded'
        ELSE 'Returned'
    END,
    NOW() - (random() * INTERVAL '180 days')
FROM generate_series(1, 3000);

----------------------------------------------------
-- ORDER ITEMS
----------------------------------------------------

INSERT INTO order_items (order_id, product_id, quantity, price)
SELECT
    o.id,
    (random() * 999)::int + 1,
    (random() * 3)::int + 1,
    ROUND((20 + random() * 300)::numeric, 2)
FROM orders o
CROSS JOIN generate_series(1, 4)
WHERE random() < 0.7;

----------------------------------------------------
-- UPDATE TOTALS
----------------------------------------------------

UPDATE orders o
SET total_price = sub.total
FROM (
    SELECT order_id, SUM(quantity * price) AS total
    FROM order_items
    GROUP BY order_id
) sub
WHERE sub.order_id = o.id;
