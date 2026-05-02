FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    alembic \
    fastapi \
    pydantic \
    pydantic-settings \
    psycopg[binary] \
    sqlalchemy \
    uvicorn

COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini

ENV PYTHONPATH=/app/src
ENV KJ_ATLAS_DATABASE_URL=postgresql+asyncpg://kj_atlas:kj_atlas@db:5432/kj_atlas
ENV KJ_ATLAS_LLM_PROVIDER=none

EXPOSE 8000

CMD ["uvicorn", "kj_atlas_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
