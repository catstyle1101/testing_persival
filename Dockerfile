FROM python:alpine

WORKDIR /app

COPY ./superlists/requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt
