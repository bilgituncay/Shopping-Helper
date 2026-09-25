from datetime import datetime
from pydantic import BaseModel

class ProductMatch(BaseModel):
    id: int
    name: str
    category: str

    class Config:
        from_attributes = True

class ReviewOut(BaseModel):
    source: str
    rating: float
    review_count: int
    url: str | None

    class Config:
        from_attributes = True

class SearchResultItem(BaseModel):
    product_id: int
    name: str
    category: str
    price: float | None
    retailer: str | None
    scraped_at: datetime | None
    avg_rating: float | None
    rating_diff: float | None
    source_count: int
    reviews: list[ReviewOut]

class SearchResponse(BaseModel):
    baseline: SearchResultItem
    results: list[SearchResultItem]
    limit: int
    offset: int
    total: int