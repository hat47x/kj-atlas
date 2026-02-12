from secrets import compare_digest

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from kj_atlas_api.db import init_db
from kj_atlas_api.routes.ai import router as ai_router
from kj_atlas_api.routes.docs import router as docs_router
from kj_atlas_api.settings import settings

app = FastAPI(title="kj-atlas API")


@app.middleware("http")
async def require_api_key(request: Request, call_next):
    if request.url.path == "/healthz":
        return await call_next(request)

    if settings.api_key:
        provided_key = request.headers.get("x-api-key")
        if not provided_key or not compare_digest(provided_key, settings.api_key):
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    return await call_next(request)


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
