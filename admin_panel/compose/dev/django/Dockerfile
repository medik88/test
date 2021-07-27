FROM python:3.9-slim-buster

RUN apt update \
    && apt install -y build-essential libpq-dev gettext

EXPOSE 8000/tcp
WORKDIR /app

# Копируем только requirements, остальное в volume bind для удобства разработки
COPY ./movies_admin/requirements /requirements
RUN pip install pip -U && pip install -r /requirements/dev.txt

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
