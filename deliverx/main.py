from pathlib import Path

from fastapi import FastAPI
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

root_router = APIRouter(prefix="/rest/api")
STATIC_DIR = Path(__file__).resolve().parent / "static"


def import_order():
    from deliverx.api.internal import router as internal_router
    from deliverx.api.notifications_controller import router as notifications_router

    root_router.include_router(internal_router)
    root_router.include_router(notifications_router)


import_order()

app = FastAPI(
    title="Devliver[X]",
    description="A sophisticated distributed notification system",
    version="1.0",
    docs_url="/",
)

app.include_router(root_router)


@app.get("/ui", include_in_schema=False)
def ui_redirect():
    return RedirectResponse(url="/ui/")


app.mount("/ui", StaticFiles(directory=STATIC_DIR, html=True), name="ui")
