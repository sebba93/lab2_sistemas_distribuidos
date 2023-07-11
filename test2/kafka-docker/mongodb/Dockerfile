FROM python:3.10-slim-buster

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "./consumer.py" ]
