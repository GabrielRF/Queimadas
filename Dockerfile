FROM python:3.11-alpine

RUN apk add firefox
RUN mkdir /usr/src/queimadas

WORKDIR /usr/src/queimadas

COPY requirements.txt requirements.txt
COPY filenames.db filenames.db
COPY queimadas.py queimadas.py

VOLUME ./filenames.db /usr/src/filenames.db

RUN pip install -r requirements.txt
CMD ["python", "./queimadas.py"]
