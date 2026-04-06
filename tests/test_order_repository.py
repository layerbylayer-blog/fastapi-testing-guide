"""Repository tests: hit the test database directly, no HTTP layer."""
import pytest
from uuid import uuid4

from app.repositories.order_repository import OrderRepository


@pytest.fixture
def order_repo(db_session):
    return OrderRepository(session=db_session)


async def test_create_and_get(order_repo):
    product_id = uuid4()
    created = await order_repo.create(product_id=product_id, quantity=5)

    assert created.id is not None
    assert created.product_id == product_id
    assert created.quantity == 5
    assert created.status == "pending"

    fetched = await order_repo.get(created.id)
    assert fetched is not None
    assert fetched.id == created.id


async def test_get_nonexistent(order_repo):
    result = await order_repo.get(uuid4())
    assert result is None


async def test_update_status(order_repo):
    order = await order_repo.create(product_id=uuid4(), quantity=1)

    updated = await order_repo.update_status(order.id, "confirmed")

    assert updated is not None
    assert updated.status == "confirmed"


async def test_list_all(order_repo):
    await order_repo.create(product_id=uuid4(), quantity=1)
    await order_repo.create(product_id=uuid4(), quantity=2)

    orders = await order_repo.list_all()
    assert len(orders) == 2
