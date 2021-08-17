FROM python:slim

COPY . /lanews

WORKDIR /lanews

RUN python3 -m venv venv && \
    venv/bin/pip install -r requirements.txt

CMD ["venv/bin/python", "main.py"]