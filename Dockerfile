FROM python:3.11.3-alpine3.17
COPY . /app
WORKDIR /app

# Install OS Package ============================================================
RUN apk update
RUN apk --no-cache add curl
RUN apk --no-cache add bash

# Install Python Package =========================================================
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

# Entrypoint =====================================================================
CMD gunicorn --timeout 300 --bind 0.0.0.0:5000 --workers 3 --log-level "info" run:app

