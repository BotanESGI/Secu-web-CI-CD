# Secu-web-CI-CD
# Contact Manager - Application CLI avec vulnérabilités intentionnelles

## Description

Application CLI de gestion de contacts développée en Python. L'application permet de gérer une liste de contacts (ajout, modification, suppression, recherche) avec des fonctionnalités d'export/import de données. 

L'application contient intentionnellement plusieurs vulnérabilités de sécurité (SQL Injection, Path Traversal, XSS, secrets en dur, dépendances vulnérables) pour des besoins pédagogiques.

## Répartition des tâches

### Botan : Infrastructure et base de données

- Créer la structure du projet (dossiers, fichiers de base)
- Implémenter la gestion de la base de données avec injection SQL vulnérable
  - Connexion SQLite
  - Fonctions CRUD (Create, Read, Update, Delete) avec requêtes SQL non paramétrées
  - Recherche de contacts vulnérable à SQLi
- Créer le Dockerfile (avec dépendances vulnérables)
- Créer `requirements.txt` avec versions vulnérables (Flask, requests, etc.)
- Tests unitaires pour la base de données (`tests/test_database.py`)

### Aya : Gestion des fichiers et Path Traversal

- Implémenter la gestion des fichiers contacts
  - Export/import de contacts en JSON/CSV
  - Sauvegarde/restauration de données
  - Path Traversal vulnérable (lecture/écriture sans validation)
- Gestion des secrets en dur (tokens API, mots de passe dans le code)
- Tests unitaires pour la gestion de fichiers (`tests/test_file_handler.py`)

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


