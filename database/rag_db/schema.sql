CREATE EXTENSION IF NOT EXISTS vector;

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
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    chunk_index INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

----------------------------------------------------
-- INDEXES
----------------------------------------------------

CREATE INDEX idx_document_chunks_document ON document_chunks(document_id);
