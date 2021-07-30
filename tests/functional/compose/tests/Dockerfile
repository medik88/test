FROM python:3.9-slim-buster

WORKDIR /tests

COPY ./requirements.txt /requirements.txt
RUN pip install pip -U && pip install -r /requirements.txt

COPY . /functional
