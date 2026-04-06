"""Unit tests for business logic: mock the repository, test the service."""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from app.services.order_service import OrderService
from app.models import Order


@pytest.fixture
def mock_order_repo():
    return AsyncMock()


@pytest.fixture
def order_service(mock_order_repo):
    return OrderService(order_repo=mock_order_repo)


async def test_create_order_success(order_service, mock_order_repo):
    product_id = uuid4()
    mock_order_repo.create.return_value = Order(
        id=uuid4(),
        product_id=product_id,
        quantity=2,
        status="pending"
    )

    result = await order_service.create_order(product_id=product_id, quantity=2)

    assert result.status == "pending"
    mock_order_repo.create.assert_called_once_with(
        product_id=product_id, quantity=2
    )


async def test_create_order_zero_quantity(order_service):
    with pytest.raises(ValueError, match="quantity must be positive"):
        await order_service.create_order(product_id=uuid4(), quantity=0)


async def test_create_order_negative_quantity(order_service):
    with pytest.raises(ValueError, match="quantity must be positive"):
        await order_service.create_order(product_id=uuid4(), quantity=-5)


async def test_cancel_order_already_shipped(order_service, mock_order_repo):
    order_id = uuid4()
    mock_order_repo.get.return_value = Order(
        id=order_id,
        product_id=uuid4(),
        quantity=1,
        status="shipped"
    )

    with pytest.raises(ValueError, match="cannot cancel"):
        await order_service.cancel_order(order_id=order_id)


async def test_cancel_order_not_found(order_service, mock_order_repo):
    mock_order_repo.get.return_value = None

    with pytest.raises(ValueError, match="not found"):
        await order_service.cancel_order(order_id=uuid4())


@pytest.mark.parametrize("status", ["pending", "confirmed", "processing"])
async def test_cancel_valid_statuses(order_service, mock_order_repo, status):
    order_id = uuid4()
    order = Order(id=order_id, product_id=uuid4(), quantity=1, status=status)
    mock_order_repo.get.return_value = order
    mock_order_repo.update_status.return_value = Order(
        id=order_id, product_id=uuid4(), quantity=1, status="cancelled"
    )

    result = await order_service.cancel_order(order_id=order_id)

    assert result.status == "cancelled"
    mock_order_repo.update_status.assert_called_once_with(order_id, "cancelled")


@pytest.mark.parametrize("status", ["shipped", "delivered", "cancelled"])
async def test_cancel_invalid_statuses(order_service, mock_order_repo, status):
    order_id = uuid4()
    mock_order_repo.get.return_value = Order(
        id=order_id, product_id=uuid4(), quantity=1, status=status
    )

    with pytest.raises(ValueError, match="cannot cancel"):
        await order_service.cancel_order(order_id=order_id)
