from shared.database import sync_engine
from sqlalchemy import text

with sync_engine.begin() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
    conn.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_products_name_trgm "
        "ON products USING GIN (name gin_trgm_ops);"
    ))
print("pg_trgm extension enabled and trigram index created.")