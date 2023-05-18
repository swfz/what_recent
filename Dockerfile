FROM python:3

WORKDIR /app

RUN apt-get update

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install --upgrade pipenv
