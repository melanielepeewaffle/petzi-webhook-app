import os
import hmac
import hashlib
import time
import json

# ⚠️ Mets ici la même clé secrète que dans `app.py`
SECRET = os.getenv("PETZI_SECRET", "default_secret")  # Valeur par défaut en cas d'absence

def generate_signature(body):
    timestamp = str(int(time.time()))  # Générer un timestamp actuel
    body_to_sign = f"{timestamp}.{body}".encode()
    signature = hmac.new(SECRET.encode(), body_to_sign, hashlib.sha256).hexdigest()
    return timestamp, signature

# Exemple de données JSON
data = json.dumps({
    "event": "ticket_created",
    "details": {
        "ticket": {
            "number": "12345",
            "title": "Concert"
        }
    }
})

timestamp, signature = generate_signature(data)
print(f"JSON utilisé pour la signature: {data}")
print(f"Timestamp: {timestamp}")
print(f"Signature: {signature}")