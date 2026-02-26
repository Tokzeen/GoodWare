# Utilise une image Python légère
FROM python:3.11-slim

# Crée un dossier pour l'app
WORKDIR /app

# Copie les fichiers de l'application
COPY app/ /app/

# Installe les dépendances système nécessaires
RUN apt-get update && \
    apt-get install -y gcc build-essential libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# Installe les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Expose le port Flask
EXPOSE 5000

# Démarre le serveur Flask (avec -u pour logs immédiats)
CMD ["python", "-u", "server.py"]
