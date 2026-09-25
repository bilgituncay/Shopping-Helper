from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_db
from shared.models import Product, PriceSnapshot, Review
from shared.schemas import ProductMatch, SearchResultItem, SearchResponse, ReviewOut

app = FastAPI(title="Shopper Helper API")

@app.get("/health/live")
async def health_live():
    return {"status": "alive"}

@app.get("/health/ready")
async def health_ready(db:AsyncSession = Depends(get_async_db)):
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="Database not reachable")
    return {"status": "ready"}

async def get_latest_price(db: AsyncSession, product_id: int) -> PriceSnapshot | None:
    stmt = (
        select(PriceSnapshot)
        .where(PriceSnapshot.product_id == product_id)
        .order_by(PriceSnapshot.scraped_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_latest_prices_in_range(
        db: AsyncSession, category: str, price_min: float, price_max: float, exclude_id: int
) -> dict[int, PriceSnapshot]:
    stmt = (
        select(PriceSnapshot)
        .join(Product, Product.id == PriceSnapshot.product_id)
        .where(Product.category == category, Product.id != exclude_id)
        .distinct(PriceSnapshot.product_id)
        .order_by(PriceSnapshot.product_id, PriceSnapshot.scraped_at.desc())
    )
    result = await db.execute(stmt)
    snapshots = result.scalars().all()
    return {
        s.product_id: s for s in snapshots if price_min <= s.price <= price_max
    }

async def get_rating_summary(db: AsyncSession, product_id: int) -> tuple[float | None, int]:
    stmt = select(func.avg(Review.rating), func.count(Review.id)).where(
        Review.product_id == product_id
    )
    result = await db.execute(stmt)
    avg_rating, count = result.one()
    return avg_rating, count


async def get_reviews(db: AsyncSession, product_id: int) -> list[Review]:
    stmt = select(Review).where(Review.product_id == product_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_rating_summaries_batch(db: AsyncSession , product_ids: list) -> dict[int, tuple[float | None, int]]:
    if not product_ids:
        return {}
    stmt = (
        select(Review.product_id, func.avg(Review.rating), func.count(Review.id))
        .where(Review.product_id.in_(product_ids))
        .group_by(Review.product_id)
        )
    result = await db.execute(stmt)
    return {pid: (avg, count) for pid, avg, count in result.all()}

async def get_reviews_batch(db: AsyncSession, product_ids: list) -> dict[int, list[Review]]:
    if not product_ids:
        return {}
    stmt = select(Review).where(Review.product_id.in_(product_ids))
    result = await db.execute(stmt)
    grouped: dict[int, list[Review]] = {pid: [] for pid in product_ids}
    for review in result.scalars().all():
        grouped[review.product_id].append(review)
    return grouped

@app.get("/products/match", response_model=list[ProductMatch])
async def match_products(
    q: str,
    category: str | None = None,
    limit: int = Query(default=10, le=25),
    db: AsyncSession = Depends(get_async_db),
):
    stmt = select(Product, func.similarity(Product.name, q).label("sim")).where(
        func.similarity(Product.name, q) > 0.2
    )
    if category:
        stmt = stmt.where(Product.category == category)
    stmt = stmt.order_by(text("sim DESC")).limit(limit)

    result = await db.execute(stmt)
    rows = result.all()
    return [row[0] for row in rows]

@app.get("/search", response_model=SearchResponse)
async def search(
    product_id: int,
    price_range: float = 5.0,
    limit: int = Query(default=20, le=100),
    offset: int = 0,
    db: AsyncSession = Depends(get_async_db)
):
    baseline_product = await db.get(Product, product_id)
    if baseline_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    baseline_price = await get_latest_price(db, product_id)
    if baseline_price is None:
        raise HTTPException(status_code=404, detail="No price data for this product yet.")
    
    baseline_avg_rating, baseline_review_count = await get_rating_summary(db, product_id)
    baseline_reviews = await get_reviews(db, product_id)

    baseline_item = SearchResultItem(
        product_id=baseline_product.id,
        name=baseline_product.name,
        category=baseline_product.category,
        price=baseline_price.price,
        retailer=baseline_price.retailer,
        scraped_at=baseline_price.scraped_at,
        avg_rating=baseline_avg_rating,
        rating_diff=0.0,
        source_count=baseline_review_count,
        reviews=[ReviewOut.model_validate(r) for r in baseline_reviews],
    )

    price_min = baseline_price.price - price_range
    price_max = baseline_price.price + price_range

    candidate_prices = await get_latest_prices_in_range(
        db, baseline_product.category, price_min, price_max, exclude_id=product_id
    )
    print("DEBUG candidate_prices:", {pid: s.price for pid, s in candidate_prices.items()})

    candidate_ids = list(candidate_prices.keys())
    candidates_stmt = select(Product).where(Product.id.in_(candidate_ids))
    candidates_result = await db.execute(candidates_stmt)
    candidate_products = {p.id: p for p in candidates_result.scalars().all()}

    rating_summaries = await get_rating_summaries_batch(db, candidate_ids)
    reviews_by_product = await get_reviews_batch(db, candidate_ids)

    results: list[SearchResultItem] = []
    for pid, snapshot in candidate_prices.items():
        product = candidate_products.get(pid)
        if product is None:
            continue
        avg_rating, review_count = rating_summaries.get(pid, (None, 0))
        reviews = reviews_by_product.get(pid, [])
        rating_diff = (
            avg_rating - baseline_avg_rating
            if avg_rating is not None and baseline_avg_rating is not None
            else None
        )
        results.append(
            SearchResultItem(
                product_id=product.id,
                name=product.name,
                category=product.category,
                price=snapshot.price,
                retailer=snapshot.retailer,
                scraped_at=snapshot.scraped_at,
                avg_rating=avg_rating,
                rating_diff=rating_diff,
                source_count=review_count,
                reviews=[ReviewOut.model_validate(r) for r in reviews],
            )
        )
    results.sort(
        key=lambda r: (r.avg_rating or 0, r.source_count),
        reverse=True,
    )

    total = len(results)
    paginated = results[offset: offset + limit]

    return SearchResponse(
        baseline=baseline_item,
        results=paginated,
        limit=limit,
        offset=offset,
        total=total,
    )