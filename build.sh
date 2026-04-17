#!/usr/bin/env bash
set -o errexit

cd studyflow
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
