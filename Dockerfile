FROM python:3.8-slim-buster

RUN apt-get update
RUN apt-get install -y bash

ADD entrypoint.sh /
ADD requirements.txt /
ADD main.py /

RUN pip install -r /requirements.txt
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
