from fastapi import FastAPI
from fastapi import APIRouter

root_router = APIRouter(prefix="/rest/api")


def import_order():
    from deliverx.api.internal import router as internal_router
    from deliverx.api.producer import router as producer_router

    root_router.include_router(internal_router)
    root_router.include_router(producer_router)


import_order()

app = FastAPI(
    title="Devliver[X]",
    description="A sophisticated distributed notification system",
    version="1.0",
    docs_url="/"
)

app.include_router(root_router)
