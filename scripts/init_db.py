from sqlalchemy import text

from shared.database import sync_engine
from shared.models import Base

def init_db():
    with sync_engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))

    Base.metadata.create_all(sync_engine)

    with sync_engine.begin() as conn:
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_products_name_trgm "
            "ON products USING GIN (name gin_trgm_ops);"
        ))

    print("Database initialised: extension, tables, and trigram index are in place.")

if __name__ == "__main__":
    init_db()