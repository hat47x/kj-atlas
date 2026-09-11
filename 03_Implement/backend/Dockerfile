FROM python:3.12-slim

WORKDIR /app

# Single source of truth: app deps (incl. the fastapi<0.137 cap) come from pyproject.toml.
# psycopg[binary] is added explicitly because it is the Postgres driver for this Docker
# path only; the non-Docker path uses sqlite, so it is intentionally absent from pyproject.
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir . "psycopg[binary]"

COPY alembic ./alembic
COPY alembic.ini ./alembic.ini

ENV PYTHONPATH=/app/src
ENV SUI_DATABASE_URL=postgresql+asyncpg://sui_sensemaking:sui_sensemaking@db:5432/sui_sensemaking
ENV SUI_LLM_PROVIDER=none

EXPOSE 8000

CMD ["uvicorn", "sui_sensemaking_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
