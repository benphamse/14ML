-- Enable extensions useful for 100k+ user scenario
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";      -- trigram index for text search
CREATE EXTENSION IF NOT EXISTS "btree_gin";     -- GIN index for scalars
