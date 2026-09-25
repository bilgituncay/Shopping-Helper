from shared.database import sync_engine
from shared.models import Base
from sqlalchemy import text

Base.metadata.create_all(sync_engine)
print('Tables created.')

with sync_engine.connect() as conn:
    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
    print('Tables in DB:', sorted(row[0] for row in result))