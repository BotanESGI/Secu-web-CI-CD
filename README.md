# Secu-web-CI-CD
# Contact Manager - Application CLI avec vulnérabilités intentionnelles

## Description

Application CLI de gestion de contacts développée en Python. L'application permet de gérer une liste de contacts (ajout, modification, suppression, recherche) avec des fonctionnalités d'export/import de données. 

L'application contient intentionnellement plusieurs vulnérabilités de sécurité (SQL Injection, Path Traversal, XSS, secrets en dur, dépendances vulnérables) pour des besoins pédagogiques.

## Répartition des tâches

### Botan : Infrastructure et base de données

- ✅ Créer la structure du projet (dossiers, fichiers de base)
- ✅ Implémenter la gestion de la base de données avec injection SQL vulnérable
  - ✅ Connexion SQLite
  - ✅ Fonctions CRUD (Create, Read, Update, Delete) avec requêtes SQL non paramétrées
  - ✅ Recherche de contacts vulnérable à SQLi
- ✅ Créer le Dockerfile (avec dépendances vulnérables)
- ✅ Créer `requirements.txt` avec versions vulnérables (Flask, requests, etc.)
- ✅ Tests unitaires pour la base de données (`tests/test_database.py`)


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

Le module `app/database.py` est vulnérable à l’injection SQL pour les besoins :

- Les requêtes sont construites par **concaténation de chaînes** / f-strings (sans paramètres préparés).
- Les valeurs utilisateur (nom, email, notes, etc.) sont injectées directement dans la requête SQL.
- La fonction `search_contacts()` permet de tester facilement des payloads SQLi, par exemple : `"' OR 1=1 --"`.

### Commandes pour tester avec Docker

```bash
# Construire l'image
docker build -t contacts-vuln .

# Lancer les tests dans le conteneur
docker run --rm contacts-vuln
```

Si tout est correct, les tests de la base de données (`tests/test_database.py`) doivent passer (`5 passed`)

### Aya : Gestion des fichiers et Path Traversal

- ✅ Implémenter la gestion des fichiers contacts
  - ✅ Export/import de contacts en JSON/CSV
  - ✅ Sauvegarde/restauration de données
  - ✅ Path Traversal vulnérable (lecture/écriture sans validation)
- ✅ Gestion des secrets en dur (tokens API, mots de passe dans le code)
- ✅ Tests unitaires pour la gestion de fichiers (`tests/test_file_handler.py`)

#### Structure

- `app/file_handler.py` : module de gestion des fichiers (export/import JSON/CSV, sauvegarde/restauration)
- `app/config.py` : module de configuration avec secrets en dur (tokens API, mots de passe, clés)
- `tests/test_file_handler.py` : tests unitaires pour la gestion des fichiers (9 tests)

#### Fonctionnalités

Le module `file_handler.py` fournit :

- `export_contacts_json(output_path)` : exporte tous les contacts au format JSON
- `export_contacts_csv(output_path)` : exporte tous les contacts au format CSV
- `import_contacts_json(input_path)` : importe des contacts depuis un fichier JSON
- `import_contacts_csv(input_path)` : importe des contacts depuis un fichier CSV
- `save_backup(backup_path)` : sauvegarde la base de données complète dans un fichier JSON
- `restore_backup(backup_path)` : restaure la base de données depuis un fichier de sauvegarde

Le module `config.py` contient :

- Secrets en dur : `API_TOKEN`, `API_SECRET_KEY`, `DB_PASSWORD`, `JWT_SECRET`, `AWS_ACCESS_KEY_ID`, `ADMIN_PASSWORD`, `GITHUB_TOKEN`, etc.
- Configuration de l'application : `APP_NAME`, `APP_VERSION`, `DEBUG_MODE`

#### Vulnérabilités Path Traversal

Le module `app/file_handler.py` est vulnérable au Path Traversal :

- **Aucune validation des chemins de fichiers** : les fonctions acceptent n'importe quel chemin sans vérification
- Permet d'écrire/lire des fichiers en dehors du répertoire prévu
- Exemple d'abus : `"../../../etc/passwd"` peut être utilisé pour accéder à des fichiers système
- Les chemins sont utilisés directement sans normalisation ou validation

#### Exécution des tests

**Tests locaux :**
```bash
# Exécuter tous les tests
python3 -m pytest tests/ -v

# Exécuter uniquement les tests de file_handler
python3 -m pytest tests/test_file_handler.py -v

# Exécuter avec plus de détails
python3 -m pytest tests/test_file_handler.py -vv
```

**Tests avec Docker :**
```bash
# Construire l'image
docker build -t contacts-vuln .

# Exécuter tous les tests (inclut test_file_handler.py)
docker run --rm contacts-vuln

# Résultat attendu : 14 passed (5 pour database + 9 pour file_handler)
```

**Tests spécifiques :**
```bash
# Tester uniquement l'export JSON
python3 -m pytest tests/test_file_handler.py::test_export_contacts_json -v

# Tester la vulnérabilité Path Traversal
python3 -m pytest tests/test_file_handler.py::test_path_traversal_vulnerability_json -v
```

**Résultats attendus :**
- 9 tests pour `test_file_handler.py` doivent tous passer
- Tests couvrant : export JSON/CSV, import JSON/CSV, sauvegarde/restauration, Path Traversal, base vide

### Meryem : Interface CLI et XSS/affichage

- Créer l'interface CLI principale (`app.py` ou `cli.py`)
  - Menu interactif
  - Commandes (ajouter, lister, rechercher, modifier, supporter)
  - Affichage des données (vulnérable à XSS si export HTML)
- Implémenter l'export HTML avec XSS potentiel
- Créer les tests principaux (`tests/test_app.py`)
- Documentation de base (README.md)

## Structure du projet

```
contact-manager/
├── app/
│   ├── __init__.py
│   ├── cli.py              # Interface CLI principale
│   ├── database.py         # Gestion de la base de données
│   ├── file_handler.py     # Gestion des fichiers
│   └── config.py           # Configuration (secrets en dur)
├── tests/
│   ├── __init__.py
│   ├── test_database.py    # Tests pour la base de données
│   ├── test_file_handler.py # Tests pour la gestion de fichiers
│   └── test_app.py         # Tests pour l'application CLI
├── data/                   # Base de données et fichiers
├── requirements.txt        # Dépendances Python
└── README.md               # Documentation
```

## Prérequis

- Python 3.8, 3.9 ou 3.10
- pip


## Utilisation

```bash
# Lancer l'application CLI
python app/cli.py
```

## Fonctionnalités

- Ajout, modification, suppression de contacts
- Recherche de contacts
- Export/import de contacts (JSON, CSV, HTML)
- Sauvegarde et restauration de données

## Vulnérabilités intentionnelles

Cette application contient intentionnellement des vulnérabilités pour les besoins pédagogiques :

- **SQL Injection** : Requêtes SQL non paramétrées dans les fonctions de recherche
- **Path Traversal** : Validation insuffisante des chemins de fichiers lors de l'export/import
- **XSS** : Affichage non sécurisé de données utilisateur dans l'export HTML
- **Secrets en dur** : Tokens et mots de passe stockés directement dans le code
- **Dépendances vulnérables** : Versions obsolètes de bibliothèques dans `requirements.txt`


