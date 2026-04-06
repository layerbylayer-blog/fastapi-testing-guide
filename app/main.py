from fastapi import FastAPI
from app.routers.orders import router as orders_router

app = FastAPI(title="FastAPI Testing Guide")

app.include_router(orders_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
