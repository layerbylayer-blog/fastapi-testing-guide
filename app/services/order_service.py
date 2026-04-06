import uuid
from app.repositories.order_repository import OrderRepositoryProtocol
from app.models import Order

CANCELLABLE_STATUSES = {"pending", "confirmed", "processing"}


class OrderService:
    def __init__(self, order_repo: OrderRepositoryProtocol):
        self.order_repo = order_repo

    async def create_order(self, product_id: uuid.UUID, quantity: int) -> Order:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        return await self.order_repo.create(product_id=product_id, quantity=quantity)

    async def get_order(self, order_id: uuid.UUID) -> Order | None:
        return await self.order_repo.get(order_id)

    async def cancel_order(self, order_id: uuid.UUID) -> Order:
        order = await self.order_repo.get(order_id)
        if order is None:
            raise ValueError(f"order {order_id} not found")
        if order.status not in CANCELLABLE_STATUSES:
            raise ValueError(f"cannot cancel order with status '{order.status}'")
        return await self.order_repo.update_status(order_id, "cancelled")
