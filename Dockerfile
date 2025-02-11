# Utiliser une image de base Python 3.9
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt dans le conteneur
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste des fichiers de l'application dans le conteneur
COPY . .

# Exposer le port 5000 (port utilisé par Flask)
EXPOSE 5000

# Commande pour lancer l'application Flask
CMD ["python", "app.py"]