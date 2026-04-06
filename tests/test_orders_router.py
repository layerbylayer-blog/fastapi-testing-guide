"""Integration tests: full HTTP stack → service → repository → test database."""
import pytest
from uuid import uuid4


async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_create_order(client):
    response = await client.post("/orders", json={
        "product_id": str(uuid4()),
        "quantity": 2
    })
    assert response.status_code == 201
    data = response.json()
    assert data["quantity"] == 2
    assert data["status"] == "pending"
    assert "id" in data


async def test_get_order_not_found(client):
    response = await client.get(f"/orders/{uuid4()}")
    assert response.status_code == 404


async def test_order_roundtrip(client):
    """Create an order, fetch it, verify the data survives the round-trip."""
    product_id = str(uuid4())

    create_response = await client.post("/orders", json={
        "product_id": product_id,
        "quantity": 3
    })
    assert create_response.status_code == 201
    order_id = create_response.json()["id"]

    get_response = await client.get(f"/orders/{order_id}")
    assert get_response.status_code == 200
    assert get_response.json()["product_id"] == product_id
    assert get_response.json()["quantity"] == 3


async def test_cancel_order(client):
    create_response = await client.post("/orders", json={
        "product_id": str(uuid4()),
        "quantity": 1
    })
    order_id = create_response.json()["id"]

    cancel_response = await client.post(f"/orders/{order_id}/cancel")
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"


async def test_cancel_nonexistent_order(client):
    response = await client.post(f"/orders/{uuid4()}/cancel")
    assert response.status_code == 400


@pytest.mark.parametrize("quantity, expected_status", [
    (1,    201),   # Minimum valid quantity
    (100,  201),   # Large but valid
    (0,    422),   # Zero: Pydantic validation error
    (-1,   422),   # Negative: Pydantic validation error
    (None, 422),   # Missing field: validation error
])
async def test_create_order_quantity_validation(client, quantity, expected_status):
    payload = {"product_id": str(uuid4())}
    if quantity is not None:
        payload["quantity"] = quantity

    response = await client.post("/orders", json=payload)
    assert response.status_code == expected_status


async def test_test_isolation(client):
    """Verify that each test starts with an empty database (rollback works)."""
    # If isolation works, there are no leftover orders from previous tests
    response = await client.post("/orders", json={
        "product_id": str(uuid4()),
        "quantity": 1
    })
    assert response.status_code == 201
    # The order was created fresh — no ghost data from other tests
