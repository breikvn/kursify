# Django Backend (Python)
FROM python:3.11-slim

# Arbeitsverzeichnis im Container
WORKDIR /app

# Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code kopieren
COPY . .

# Django Dev Server starten
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
