FROM python:3.7-slim

RUN mkdir /app
WORKDIR /app
COPY ./ /app
RUN pip3 install -r requirements.txt
