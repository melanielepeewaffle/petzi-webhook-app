# Serveur Flask qui écoutera les requêtes POST du webhook
import logging
import os
from flask import Flask, request, jsonify
import hmac
import hashlib
import datetime
import psycopg2

app = Flask(__name__)

# Clé secrète partagée avec Petzi (à configurer dans l'interface Petzi)
SECRET = os.getenv("PETZI_SECRET", "default_secret")  # Valeur par défaut en cas d'absence

# Configuration de la base de données
DB_CONFIG = {
    "dbname": "petzi_db",
    "user": "user",
    "password": "password",
    "host": "db",  # "db" est le nom du service dans docker-compose.yml
    "port": "5432"
}


def save_to_db(data):
    """
    Sauvegarde les données du webhook dans la base de données.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tickets (ticket_number, event_name, buyer_name)
            VALUES (%s, %s, %s)
        """, (data["details"]["ticket"]["number"], data["details"]["ticket"]["event"], data["details"]["buyer"]["firstName"]))
        conn.commit()
    except Exception as e:
        conn.rollback()
        logging.error(f"Erreur lors de la sauvegarde des données dans la base de données : {e}")
    finally:
        cursor.close()
        conn.close()

def verify_signature(signature, body):
    """
    Vérifie la signature de la requête webhook.
    """
    try:
        # Extraire le timestamp et la signature de l'en-tête
        parts = dict(part.split("=") for part in signature.split(","))
        timestamp = parts["t"]
        received_signature = parts["v1"]

        # Préparer la chaîne à signer
        body_to_sign = f"{timestamp}.{body}".encode()

        # Calculer la signature attendue
        expected_signature = hmac.new(SECRET.encode(), body_to_sign, hashlib.sha256).hexdigest()

        # Comparer les signatures (en utilisant une comparaison constante pour éviter les attaques par timing)
        if not hmac.compare_digest(expected_signature, received_signature):
            return False

        # Vérifier que le timestamp n'est pas trop ancien (max 30 secondes)
        current_time = datetime.datetime.utcnow()
        message_time = datetime.datetime.fromtimestamp(int(timestamp))
        time_delta = (current_time - message_time).total_seconds()

        if time_delta > 30:
            return False

        return True

    except Exception as e:
        print(f"Erreur lors de la vérification de la signature : {e}")
        return False

@app.route('/')
def home():
    return "Bienvenue sur l'API de Webhooks ! Utilisez POST pour envoyer des webhooks à /webhook."

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Endpoint pour recevoir les webhooks de Petzi.
    """
    # Récupérer la signature et le corps de la requête
    signature = request.headers.get('Petzi-Signature')
    if not signature:
        return jsonify({"error": "Signature manquante"}), 400

    #body = request.get_data(as_text=True)

    # Vérifier la signature
    #if not verify_signature(signature, body):
    #    return jsonify({"error": "Signature invalide"}), 401

    # Traiter les données du webhook
    data = request.json
    print("Données reçues :", data)  # À remplacer par la logique de persistance

    # Sauvegarder les données dans la base de données
    save_to_db(data)

    # Répondre avec un succès
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)