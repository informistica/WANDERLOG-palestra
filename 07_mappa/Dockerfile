FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# gettext serve per i18n (compilemessages)
RUN apt-get update && apt-get install -y --no-install-recommends gettext && rm -rf /var/lib/apt/lists/*

# Prima le dipendenze: Docker riusa questo layer finché i requirements non cambiano
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# Poi il codice
COPY . .

WORKDIR /app/palestra

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
