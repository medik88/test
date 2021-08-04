FROM fastapi_image

WORKDIR /tests

COPY . /tests

RUN pip install pip -U && pip install -r /tests/functional/requirements.txt --use-feature=in-tree-build
