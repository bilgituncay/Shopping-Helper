from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False, index=True)
    specs = Column(JSON, nullable=True)
    price_snapshots = relationship(
        "PriceSnapshot", back_populates="product", cascade="all, delete-orphan"
    )
    reviews = relationship(
        "Review", back_populates="product", cascade="all, delete-orphan"
    )

class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    retailer = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    scraped_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    product = relationship("Product", back_populates="price_snapshots")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    source = Column(String, nullable=False)
    rating = Column(Float, nullable=False)
    review_count = Column(Integer, nullable=False, default=0)
    url = Column(String, nullable=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product", back_populates="reviews")
    aspects = relationship("ReviewAspect", back_populates="review", cascade="all, delete-orphan")

class ReviewAspect(Base):
    __tablename__ = "review_aspects"

    id = Column(Integer, primary_key=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False, index=True)
    aspect = Column(String, nullable=False)
    score = Column(Float, nullable=True)

    review = relationship("Review", back_populates="aspects")