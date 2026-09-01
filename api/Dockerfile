FROM python:3.12
WORKDIR /usr/src/app
RUN pip install uv
COPY ./api/uv.lock uv.lock
COPY ./api/pyproject.toml pyproject.toml
RUN uv sync
COPY ./api .
#RUN ./.venv/bin/python3.12 -m spacy download en_core_web_sm