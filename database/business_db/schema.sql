----------------------------------------------------
-- CUSTOMERS (user_id links to auth_db.users — no cross-DB FK)
----------------------------------------------------

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL UNIQUE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

----------------------------------------------------
-- PRODUCTS
----------------------------------------------------

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    price DECIMAL(10,2),
    stock INTEGER,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

----------------------------------------------------
-- ORDERS
----------------------------------------------------

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    total_price DECIMAL(10,2),
    status VARCHAR(50),
    ordered_at TIMESTAMP DEFAULT NOW()
);

----------------------------------------------------
-- ORDER ITEMS
----------------------------------------------------

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER,
    price DECIMAL(10,2)
);

----------------------------------------------------
-- INDEXES
----------------------------------------------------

CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_user_id ON customers(user_id);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_products_category ON products(category);
