from datetime import datetime

from shared.database import SyncSessionLocal
from shared.models import Product, PriceSnapshot

db = SyncSessionLocal()
try:
    product = Product(name="Generic Buds X1", category="earbuds")
    db.add(product)
    db.flush()
    db.add(
        PriceSnapshot(
            product_id=product.id,
            retailer="MediaMarkt",
            price=29.99,
            scraped_at=datetime.utcnow(),
        )
    )
    db.commit()
    print("Added product id: "), product.id
finally:
    db.close()