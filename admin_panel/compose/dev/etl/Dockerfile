FROM python:3.9-slim-buster

WORKDIR /app

COPY ./sqlite_to_postgres/requirements.txt /requirements.txt
RUN pip install pip -U && pip install -r /requirements.txt
