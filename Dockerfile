FROM python:3@sha256:0ba001803c72c128063cfa88863755f905cefabe73c026c66a5a86d8f1d63e98

WORKDIR /app

RUN apt-get update

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install --upgrade pipenv
