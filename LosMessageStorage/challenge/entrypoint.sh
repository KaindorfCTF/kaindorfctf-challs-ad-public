#!/bin/sh

cd /app/api/

psql postgresql://lms_user:lms_password@postgres_db:5432 -c "create database lms;"

pip install -r requirements.txt

python main.py
