#!/bin/sh

cd /app/testcenter/

psql postgresql://postgres:postgres@db:5432 -c "create database testcenter;"

sh util/gen_cert.sh

pip install -r requirements.txt

python app.py
