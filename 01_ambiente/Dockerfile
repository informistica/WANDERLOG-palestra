# TODO: Specifica l'immagine base Python 3.12 slim
# FROM ...

WORKDIR /app

# Installa gettext per i18n
RUN apt-get update && apt-get install -y gettext && rm -rf /var/lib/apt/lists/*

# TODO: Copia requirements.txt e installa le dipendenze Python
# COPY requirements.txt .
# RUN ...

# TODO: Copia tutto il codice del progetto
# COPY . .

WORKDIR /app/palestra

# Porta esposta per il server Django
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
