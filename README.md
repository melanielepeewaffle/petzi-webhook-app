# petzi-webhook-app
62-51.1 Urbanisation des SI (BLOC)

## Cas pratique : Case A Chocs
### Contexte
Dans le cadre de votre démarche d’architecture d’entreprise, vous êtes mandaté par la Case à chocs
pour implémenter une application serveur utilisant le webhook de petzi qui devra :
1. Vérifier l’émetteur et la provenance des requêtes
2. Récupérer les informations métier contenues dans la transaction effectuée par le site de petzi
3. Persister ces informations métier pour un usage ultérieur.

Ce service sera intégré dans la vue applicative et technique cible de l’architecture d’entreprise.

### Ressources
Documentation Petzi sur Cyberlearn

### Contraintes techniques
1. Architecture orientée service. Votre service pourra être intégré dans une application composite.
2. Base de données relationnelle optionnelle, mais les données provenant de petzi doivent être persistée.
3. Utilisation docker et docker compose recommandée.

### installation et utilisation
1. Cloner le repository
2. Installer Docker et Docker Compose
3. Démarrer Docker Desktop
4. Se déplacer dans le projet (ex. : PS C:\temp> cd .\petzi-webhook-app)
5. Puis exécuter Docker Compose (ex. : PS C:\temp\petzi-webhook-app> docker-compose up -d --build)
6. Aller sur http://localhost:5000/
