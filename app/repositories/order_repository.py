import uuid
from typing import Protocol, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Order


class OrderRepositoryProtocol(Protocol):
    async def get(self, order_id: uuid.UUID) -> Order | None: ...
    async def list_all(self) -> Sequence[Order]: ...
    async def create(self, product_id: uuid.UUID, quantity: int) -> Order: ...
    async def update_status(self, order_id: uuid.UUID, status: str) -> Order | None: ...


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, order_id: uuid.UUID) -> Order | None:
        result = await self.session.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> Sequence[Order]:
        result = await self.session.execute(select(Order))
        return result.scalars().all()

    async def create(self, product_id: uuid.UUID, quantity: int) -> Order:
        order = Order(product_id=product_id, quantity=quantity)
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def update_status(self, order_id: uuid.UUID, status: str) -> Order | None:
        order = await self.get(order_id)
        if order is None:
            return None
        order.status = status
        await self.session.commit()
        await self.session.refresh(order)
        return order
