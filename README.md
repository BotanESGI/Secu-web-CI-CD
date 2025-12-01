## Partie 1 – Base de données vulnérable (SQLite / SQL Injection)

Cette partie concerne **l’infrastructure et la base de données** d’une application de gestion de contacts.

### Structure

- `app/database.py` : module de gestion de la base de données SQLite.
- `tests/test_database.py` : tests unitaires de la couche base de données.
- `requirements.txt` : dépendances Python (versions potentiellement vulnérables).
- `Dockerfile` : image Docker pour exécuter les tests dans un conteneur.

### Fonctionnalités

La base de données utilise SQLite avec une table `contacts` :

- `get_connection()` : crée/retourne une connexion vers un fichier SQLite (par défaut `contacts.db`).
- `create_contact()` : création d’un contact.
- `get_contact()` : récupération d’un contact par son `id`.
- `list_contacts()` : liste de tous les contacts.
- `update_contact()` : mise à jour de certains champs d’un contact.
- `delete_contact()` : suppression d’un contact.
- `search_contacts()` : recherche plein texte sur `name`, `email`, `notes`.

### Vulnérabilités SQL (SQL Injection)

Le module `app/database.py` est **volontairement vulnérable** à l’injection SQL pour les besoins pédagogiques :

- Les requêtes sont construites par **concaténation de chaînes** / f-strings (sans paramètres préparés).
- Les valeurs utilisateur (nom, email, notes, etc.) sont injectées directement dans la requête SQL.
- La fonction `search_contacts()` permet de tester facilement des payloads SQLi, par exemple : `"' OR 1=1 --"`.

### Commandes pour tester avec Docker

docker build -t contacts-vuln .Lancer les tests dans le conteneur :

docker run --rm contacts-vuln
Si tout est correct, les tests de la base de données (`tests/test_database.py`) doivent passer (`5 passed`)