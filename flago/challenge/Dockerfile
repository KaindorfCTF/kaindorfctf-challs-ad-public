FROM golang:1.22-alpine3.18

EXPOSE 8080

COPY flago/ /flago

WORKDIR /flago

CMD ["go", "run", "."]