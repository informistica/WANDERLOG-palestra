# TODO: immagine base Python 3.12 slim
# FROM ...

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# gettext serve per i18n (compilemessages)
RUN apt-get update && apt-get install -y --no-install-recommends gettext && rm -rf /var/lib/apt/lists/*

# TODO: copia requirements.txt e requirements-dev.txt e installa requirements-dev.txt con pip
# COPY ...
# RUN pip install ...

# TODO: copia tutto il codice del progetto
# COPY ...

WORKDIR /app/palestra

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
