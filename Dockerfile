FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir "psycopg2-binary==2.9.10"

COPY . .

# Dummy env so collectstatic works at image build time
ENV SECRET_KEY=build-time-secret \
    DEBUG=False \
    ALLOWED_HOSTS=* \
    DATABASE_URL=sqlite:////tmp/build.db

RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Railway injects $PORT
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn groupproject.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]
