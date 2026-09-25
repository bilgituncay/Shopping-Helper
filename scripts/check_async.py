import asyncio
from shared.database import AsyncSessionLocal
from shared.models import Product
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as session:
        p = Product(name="Test earbuds", category="earbuds", specs={"battery_hours": 6})
        session.add(p)
        await session.commit()
        await session.refresh(p)
        print("Inserted product id:", p.id)

        result = await session.execute(select(Product).where(Product.category == "earbuds"))
        products = result.scalars().all()
        print("Products found:", [(pr.id, pr.name, pr.specs) for pr in products]) 

if __name__ == "__main__":
        asyncio.run(main())