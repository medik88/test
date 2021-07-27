FROM python:3.9-slim-buster

RUN apt update \
    && apt install -y build-essential libpq-dev gettext

EXPOSE 8000/tcp
WORKDIR /app

# Копируем все приложение в production
COPY ./movies_admin/requirements /requirements
RUN pip install pip -U && pip install -r /requirements/production.txt
COPY ./movies_admin /app