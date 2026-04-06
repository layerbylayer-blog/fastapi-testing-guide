import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.order_repository import OrderRepository
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


class OrderCreate(BaseModel):
    product_id: uuid.UUID
    quantity: int

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("quantity must be >= 1")
        return v


class OrderResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    status: str

    model_config = {"from_attributes": True}


def get_order_service(db: AsyncSession = Depends(get_db)) -> OrderService:
    return OrderService(order_repo=OrderRepository(db))


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: uuid.UUID,
    service: OrderService = Depends(get_order_service),
):
    order = await service.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreate,
    service: OrderService = Depends(get_order_service),
):
    return await service.create_order(
        product_id=payload.product_id,
        quantity=payload.quantity,
    )


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: uuid.UUID,
    service: OrderService = Depends(get_order_service),
):
    try:
        return await service.cancel_order(order_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
