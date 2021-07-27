FROM python:3.9-slim-buster

WORKDIR /app

COPY ./postgres_to_es/requirements.txt /requirements.txt
RUN pip install pip -U && pip install -r /requirements.txt
COPY ./postgres_to_es /app