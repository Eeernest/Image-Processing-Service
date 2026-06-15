FROM python:3.14-slim

WORKDIR /core

COPY pyproject.toml ./

COPY app/ ./app/

RUN python -m pip install --no-cache-dir ".[test]"

COPY . .

ENV PYTHONPATH=/core

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"]