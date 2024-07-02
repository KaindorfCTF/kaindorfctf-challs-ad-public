FROM python:3.12.2-alpine

RUN apk update && apk add postgresql-client openssl build-base linux-headers libffi-dev

EXPOSE 5000

RUN mkdir /app

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod u+x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
