FROM python:slim

COPY . /lanews

WORKDIR /lanews

RUN python3 -m venv venv && \
    venv/bin/pip install -r requirements.txt

RUN mkdir database && \
    touch database/news.db


CMD ["venv/bin/python", "main.py"]