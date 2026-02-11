from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from kj_atlas_api.db import init_db
from kj_atlas_api.routes.ai import router as ai_router
from kj_atlas_api.routes.docs import router as docs_router

app = FastAPI(title="kj-atlas API")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.exception_handler(RequestValidationError)
def handle_validation_error(_, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": exc.errors()})


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(docs_router)
app.include_router(ai_router)
