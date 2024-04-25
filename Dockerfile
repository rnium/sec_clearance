FROM python:3.8-slim-bullseye
WORKDIR /app
RUN pip install weasyprint==60.1
RUN apt-get update \
    && apt-get install -y \
        libglib2.0-0 \
        libgirepository-1.0-1 \
        libcairo2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf2.0-0 \
        libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install qrcode
RUN pip install sendgrid