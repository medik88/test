FROM fastapi_image

WORKDIR /tests

COPY ./requirements.txt /requirements.txt
RUN pip install pip -U && pip install -r /requirements.txt

COPY . /functional
