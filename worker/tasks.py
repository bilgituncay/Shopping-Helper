import random
from datetime import datetime
from celery import Celery
from sqlalchemy import select

from worker.celery_app import celery_app
from shared.database import SyncSessionLocal
from shared.models import Product, PriceSnapshot

@celery_app.task(name="refresh_price")
def refresh_price(product_id: int) -> dict:
    db = SyncSessionLocal()
    try:
        product = db.get(Product, product_id)
        if product is None:
            return {"status": "error", "detail": f"Product {product_id} not found"}
        
        latest = (
            db.query(PriceSnapshot)
            .filter(PriceSnapshot.product_id == product_id)
            .order_by(PriceSnapshot.scraped_at.desc())
            .first()
        )
        base_price = latest.price if latest else 30.0
        retailer = latest.retailer if latest else "MediaMarkt"

        # Placeholder: jitter the price slightly to simulate a real price check.
        # Will be replaced once a real price-comparison API is wired up.
        jitter = random.uniform(-2.0, 2.0)
        new_price = round(max(base_price + jitter, 0.01), 2)

        snapshot = PriceSnapshot(
            product_id=product_id,
            retailer=retailer,
            price=new_price,
            scraped_at=datetime.utcnow()
        )
        db.add(snapshot)
        db.commit()

        return {"status": "ok", "product_id": product_id, "new_price": new_price}
    finally:
        db.close()

@celery_app.task(name="refresh_all_prices")
def refresh_all_prices() -> dict:
    db = SyncSessionLocal()
    try:
        product_ids = [pid for (pid,) in db.query(Product.id).all()]
    finally:
        db.close()

    for pid in product_ids:
        refresh_price.delay(product_id=pid)

    return {"status": "ok", "enqueued": len(product_ids)}