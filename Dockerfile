FROM python:3.14.3-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install pipx && \
    pipx install poetry && \
    pipx ensurepath

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --only main

COPY src/ ./src/
COPY config.py alembic.ini ./
COPY migrations/ ./migrations/

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "src.presentation.main:app", "--host", "0.0.0.0", "--port", "8000"]
