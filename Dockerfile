FROM python:3.9-slim

RUN mkdir /socialhub/
RUN mkdir /socialhub/app
WORKDIR /socialhub/app

RUN apt-get update && apt-get install -y libpq-dev gcc postgresql-client

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
