FROM python:3.9-slim

WORKDIR /app
COPY ../../pyproject.toml ../../poetry.lock /app/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-dev \
    && pip uninstall -y poetry
COPY ../../src/* /app/

EXPOSE 8000

USER daemon