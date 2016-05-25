# JailStats Update Program

# FROM python:3.5.1-onbuild

FROM prolocutor/docker-python-sqlite
MAINTAINER JamesHaskell

WORKDIR /capture

COPY /capture/* /capture/
COPY requirements.txt /capture/

RUN pip install -r requirements.txt
