FROM python:3.9-alpine3.16

RUN apk --no-cache add git bash

ADD entrypoint.sh /
ADD requirements.txt /
ADD main.py /

RUN pip install --no-cache-dir -r /requirements.txt
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
