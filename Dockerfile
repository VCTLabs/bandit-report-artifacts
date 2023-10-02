FROM python:3.11-alpine3.17

RUN apk --no-cache add git bash

ADD entrypoint.sh /
ADD requirements.txt /
ADD main.py /

RUN pip install --no-cache-dir -r /requirements.txt
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
