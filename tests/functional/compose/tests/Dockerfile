FROM fastapi_image

WORKDIR /tests

COPY ./compose/tests/setup.py /tests/setup.py
COPY . /tests/functional

RUN pip install pip -U && pip install -r /tests/functional/requirements.txt --use-feature=in-tree-build
