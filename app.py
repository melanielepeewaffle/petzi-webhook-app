# Serveur Flask qui écoutera les requêtes POST du webhook
import logging
import os
from flask import Flask, json, render_template, request, jsonify
import hmac
import hashlib
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
        if not signature:
            logging.error("Aucune signature reçue")
            return False

        # Nettoyer et parser la signature
        parts = dict(part.strip().split("=") for part in signature.split(",") if "=" in part)

        if "t" not in parts or "v1" not in parts:
            logging.error("Format de signature invalide")
            return False

        timestamp = parts["t"]
        received_signature = parts["v1"]

        # Vérifier si timestamp est un entier valide
        try:
            timestamp = int(timestamp)
        except ValueError:
            logging.error("Timestamp non valide")
            return False

        # Préparer la chaîne à signer
        body_to_sign = f"{timestamp}.{body.decode('utf-8')}".encode()

        # Calculer la signature attendue
        expected_signature = hmac.new(SECRET.encode(), body_to_sign, hashlib.sha256).hexdigest()

        # Comparer les signatures en évitant les attaques par timing
        if not hmac.compare_digest(expected_signature, received_signature):
            logging.error("Signature invalide")
            return False

        return True

    except Exception as e:
        logging.error(f"Erreur lors de la vérification de la signature : {e}")
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

    # Vérifier la signature
    body = request.get_data()
    if not verify_signature(signature, body):
        return jsonify({"error": "Signature invalide"}), 401

    # Traiter les données du webhook
    data = request.json
    print("Données reçues :", data)  # À remplacer par la logique de persistance

    # Sauvegarder les données dans la base de données
    save_to_db(data)

    # Répondre avec un succès
    return jsonify({"status": "success"}), 200

@app.route('/tickets', methods=['GET'])
def get_tickets():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id, ticket_number, event_name, buyer_name FROM tickets")
        tickets = cursor.fetchall()
        conn.close()
        return jsonify([{"id": t[0], "ticket_number": t[1], "event_name": t[2], "buyer_name": t[3]} for t in tickets]), 200
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des tickets : {e}")
        return jsonify({"error": "Erreur interne"}), 500

@app.route('/dashboard')
def dashboard():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id, ticket_number, event_name, buyer_name FROM tickets")
        tickets = cursor.fetchall()
        conn.close()
        
        # Transformer les tuples en objets JSON pour l'affichage
        tickets_json = json.dumps([{
            "id": t[0], "ticket_number": t[1], "event_name": t[2], "buyer_name": t[3]
        } for t in tickets])

        return render_template('index.html', tickets=tickets_json)
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des tickets : {e}")
        return jsonify({"error": "Erreur interne"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)