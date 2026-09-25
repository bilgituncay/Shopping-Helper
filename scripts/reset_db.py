from shared.database import sync_engine
from shared.models import Base

Base.metadata.drop_all(sync_engine)
Base.metadata.create_all(sync_engine)
print("Database reset: all tables dropped and recreated.")