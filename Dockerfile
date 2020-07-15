FROM python:latest

RUN [ -d /app] || mkdir /app

WORKDIR /app

COPY . /app
COPY ./schedule.sh /scripts/schedule.sh

RUN pip install -r requirements.txt

CMD ["scrapy-do", "-n", "scrapy-do"]