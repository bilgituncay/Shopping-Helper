from shared.database import SyncSessionLocal
from shared.models import Product, PriceSnapshot
from sqlalchemy import select

db = SyncSessionLocal()

stmt= (
    select(PriceSnapshot, Product.name)
    .join(Product, Product.id == PriceSnapshot.product_id)
    .where(Product.category == "earbuds")
    .order_by(PriceSnapshot.product_id, PriceSnapshot.scraped_at.desc())
)
rows = db.execute(stmt).all()
print("All earbuds price snapshots:")
for snapshot, name in rows:
    print(f"    product_id={snapshot.product_id} name={name} price={snapshot.price} scraped_at={snapshot.scraped_at}")

stmt2 = (
    select(PriceSnapshot)
    .join(Product, Product.id == PriceSnapshot.product_id)
    .where(Product.category == "earbuds", Product.id != 1)
    .distinct(PriceSnapshot.product_id)
    .order_by(PriceSnapshot.product_id, PriceSnapshot.scraped_at.desc())
)
rows2 = db.execute(stmt2).scalars().all()
print("\nDISTINCT ON result (excluding product_id=1):")
for s in rows2:
    print(f"    product_id={s.product_id} price={s.price}")

db.close()