# fastapi-testing-guide

Codice di riferimento per l'articolo [Testing in FastAPI: PyTest, Fixtures e Async](https://layerbylayer.dev/blog/fastapi-testing-guide) su [LayerByLayer.dev](https://layerbylayer.dev).

## Struttura

```
app/
├── main.py
├── database.py          # Engine, Base, get_db
├── models.py            # SQLAlchemy models
├── repositories/
│   └── order_repository.py
├── services/
│   └── order_service.py
└── routers/
    └── orders.py

tests/
├── conftest.py               # Fixture: engine, db_session, client
├── test_orders_router.py     # Integration tests (HTTP)
├── test_order_service.py     # Unit tests (business logic)
└── test_order_repository.py  # Repository tests (database)
```

## Quickstart

```bash
git clone https://github.com/layerbylayer-blog/fastapi-testing-guide
cd fastapi-testing-guide
pip install -r requirements-dev.txt
pytest -v
```

## Con PostgreSQL

```bash
docker compose up -d postgres-test
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/test_db pytest -v
```
