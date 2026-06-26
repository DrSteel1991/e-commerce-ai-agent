CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;

----------------------------------------------------
-- AUTH
----------------------------------------------------

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT,
    full_name VARCHAR(255),
    provider VARCHAR(50) DEFAULT 'local',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE user_roles (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY(user_id, role_id)
);

CREATE TABLE oauth_accounts (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    provider_user_id VARCHAR(255) NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(provider, provider_user_id)
);

CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

----------------------------------------------------
-- CUSTOMERS
----------------------------------------------------

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
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
-- RAG
----------------------------------------------------

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255),
    document_type VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT,
    embedding VECTOR(1536)
);

----------------------------------------------------
-- INDEXES
----------------------------------------------------

CREATE INDEX idx_customers_email
ON customers(email);

CREATE INDEX idx_orders_customer
ON orders(customer_id);

CREATE INDEX idx_orders_status
ON orders(status);

CREATE INDEX idx_order_items_order
ON order_items(order_id);

CREATE INDEX idx_products_category
ON products(category);

CREATE INDEX idx_document_chunks_document
ON document_chunks(document_id);