FROM python:3.11.3-alpine3.17
COPY . /app
WORKDIR /app

# Install OS Package ============================================================
RUN apk update
RUN apk --no-cache add curl
RUN apk --no-cache add bash

# # Cron job =======================================================================
# RUN echo "0 */1	*	*	*	/usr/local/bin/python /app/entity_cache.py" >> /var/spool/cron/crontabs/root

# Install Python Package =========================================================
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

# Entrypoint =====================================================================
CMD crond && gunicorn --timeout 300 --bind 0.0.0.0:5000 --workers 3 --log-level "info" run:app

