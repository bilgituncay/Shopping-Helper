from datetime import datetime, timedelta

from shared.database import SyncSessionLocal
from shared.models import Product, PriceSnapshot, Review, ReviewAspect


def seed():
    db = SyncSessionLocal()
    try:
        oppo = Product(
            name="OPPO Enco Buds 3",
            category="earbuds",
            specs={"battery_hours": 7, "anc": False},
        )
        sony = Product(
            name="Sony WF-C510",
            category="earbuds",
            specs={"battery_hours": 11, "anc": False},
        )
        jbl = Product(
            name="JBL Tune 130NC",
            category="earbuds",
            specs={"battery_hours": 8, "anc": True},
        )
        pricey_outlier = Product(
            name="Sennheiser Momentum True Wireless 4",
            category="earbuds",
            specs={"battery_hours": 7.5, "anc": True},
        )

        db.add_all([oppo, sony, jbl, pricey_outlier])
        db.flush()  # assigns IDs without committing yet

        now = datetime.utcnow()

        price_rows = [
            PriceSnapshot(product_id=oppo.id, retailer="MediaMarkt", price=30.0, scraped_at=now),
            PriceSnapshot(product_id=sony.id, retailer="Amazon", price=32.99, scraped_at=now - timedelta(hours=3)),
            PriceSnapshot(product_id=jbl.id, retailer="MediaMarkt", price=27.5, scraped_at=now - timedelta(hours=1)),
            # Outside the default +/-5 range around 30, to prove range filtering works
            PriceSnapshot(product_id=pricey_outlier.id, retailer="Amazon", price=179.0, scraped_at=now),
        ]
        db.add_all(price_rows)

        review_rows = [
            Review(product_id=oppo.id, source="RTINGS", rating=6.8, review_count=1, url="https://rtings.com/oppo-enco-buds-3"),
            Review(product_id=oppo.id, source="TechRadar", rating=7.0, review_count=1, url="https://techradar.com/oppo-enco-buds-3"),

            Review(product_id=sony.id, source="RTINGS", rating=7.9, review_count=1, url="https://rtings.com/sony-wf-c510"),
            Review(product_id=sony.id, source="What Hi-Fi", rating=8.1, review_count=1, url="https://whathifi.com/sony-wf-c510"),
            Review(product_id=sony.id, source="TechRadar", rating=7.7, review_count=1, url="https://techradar.com/sony-wf-c510"),

            Review(product_id=jbl.id, source="RTINGS", rating=7.2, review_count=1, url="https://rtings.com/jbl-tune-130nc"),

            Review(product_id=pricey_outlier.id, source="RTINGS", rating=8.8, review_count=1, url="https://rtings.com/sennheiser-mtw4"),
        ]
        db.add_all(review_rows)
        db.flush()

        # A couple of aspect scores, just to confirm the table works — not used in ranking yet
        aspect_rows = [
            ReviewAspect(review_id=review_rows[0].id, aspect="bass response", score=8.5),
            ReviewAspect(review_id=review_rows[0].id, aspect="battery life", score=6.0),
            ReviewAspect(review_id=review_rows[2].id, aspect="bass response", score=6.5),
        ]
        db.add_all(aspect_rows)

        db.commit()

        print("Seeded products:")
        for p in [oppo, sony, jbl, pricey_outlier]:
            print(f"  id={p.id}  {p.name}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()