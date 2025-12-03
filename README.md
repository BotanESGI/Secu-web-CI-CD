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

- ✅ Créer l'interface CLI principale (`app/cli.py`)
  - ✅ Menu interactif
  - ✅ Commandes (ajouter, lister, rechercher, modifier, supprimer)
  - ✅ Affichage des données (vulnérable à XSS si export HTML)
- ✅ Implémenter l'export HTML avec XSS potentiel
- ✅ Créer les tests principaux (`tests/test_app.py`)
- ✅ Documentation de base (README.md)

#### Structure

- `app/cli.py` : interface CLI principale avec menu interactif
- `tests/test_app.py` : tests unitaires pour l'application CLI (export HTML, fonctions CLI)

#### Fonctionnalités

L'interface CLI (`app/cli.py`) fournit un menu interactif avec les commandes suivantes :

- **1. Ajouter un contact** : crée un nouveau contact (nom, email, téléphone, notes)
- **2. Lister les contacts** : affiche tous les contacts de la base
- **3. Rechercher un contact** : recherche par mot-clé (vulnérable à SQLi)
- **4. Modifier un contact** : met à jour les informations d'un contact existant
- **5. Supprimer un contact** : supprime un contact par son ID
- **6. Exporter les contacts** : exporte au format JSON, CSV ou HTML
- **7. Importer des contacts** : importe depuis un fichier JSON ou CSV
- **8. Sauvegarde / Restauration** : sauvegarde ou restaure la base de données complète
- **0. Quitter** : ferme l'application

#### Vulnérabilité XSS (Cross-Site Scripting)

Le module `app/cli.py` contient une fonction `export_contacts_html()` qui génère un fichier HTML vulnérable à XSS :

- **Aucun échappement HTML** : les données utilisateur (nom, email, notes) sont injectées directement dans le HTML sans `html.escape()`
- Si un contact contient du code JavaScript dans ses champs (ex: `<script>alert('xss')</script>`), ce code sera exécuté lors de l'ouverture du fichier HTML dans un navigateur
- Exemple d'abus : créer un contact avec `notes = <script>alert('xss')</script>`, puis exporter en HTML et ouvrir le fichier → le script s'exécute

#### Utilisation de la CLI

**Lancer l'application :**
```bash
# Depuis le dossier du projet
python -m app.cli
```

**Exemple de test de la vulnérabilité XSS :**

1. Lancer la CLI : `python -m app.cli`
2. Choisir l'option **1** (Ajouter un contact)
3. Remplir les champs :
   - Nom : `Test XSS`
   - Email : `xss@example.com`
   - Téléphone : `123456789`
   - Notes : `<script>alert('XSS vulnérable!')</script>`
4. Choisir l'option **6** (Exporter les contacts) → **3** (Export HTML)
5. Donner un nom de fichier : `contacts.html`
6. Ouvrir `contacts.html` dans un navigateur → une alerte JavaScript devrait s'afficher

#### Exécution des tests

**Tests locaux :**
```bash
# Exécuter tous les tests (inclut test_app.py)
python -m pytest tests/ -v

# Exécuter uniquement les tests de la CLI
python -m pytest tests/test_app.py -v
```

**Tests avec Docker :**
```bash
# Construire l'image
docker build -t contacts-vuln .

# Exécuter tous les tests
docker run --rm contacts-vuln

# Résultat attendu : X passed (5 pour database + 9 pour file_handler + tests pour app)
```

**Résultats attendus :**
- Les tests de `test_app.py` doivent passer
- Tests couvrant : export HTML, génération de fichiers, vulnérabilité XSS

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

## Répartition des tâches CI/CD

### Personne 1 : Pipeline CI - Structure et Job "test"

#### ✅ Tâche 1 : Créer la structure du workflow CI
- ✅ Créer le fichier `.github/workflows/ci.yml`
- ✅ Configurer le workflow de base :
  - Nom : "CI"
  - Triggers : `push` sur `main`/`master` + trigger manuel (`workflow_dispatch`)
  - Permissions : `contents: read`, `security-events: write`, `actions: read`
  - OS : `ubuntu-latest` pour tous les jobs

#### Botan: Tâche 2 : Implémenter le job "test" - Configuration matrix et setup
- ✅ Créer le job `test` avec :
  -  Stratégie matrix pour Python 3.8, 3.9, 3.10
  -  Step "checkout" avec `actions/checkout@v5`
  -  Step "Python ${{ matrix.python-version }}" avec `actions/setup-python@v6`
  - ✅ Step "dependencies" : 
    -  Upgrade pip : `python -m pip install --upgrade pip`
    -  Installer `flake8` et `pytest`

#### Botan: Tâche 3 : Implémenter le step pytest
- ✅ Step "pytest" qui exécute les tests sur le répertoire `tests/`
- ✅ Commande : `pytest tests/`
- ✅ Vérifier que les tests passent sur les 3 versions de Python (3.8, 3.9, 3.10)

#### Botan: Tâche : Tester et valider le job "test"
- ✅ Pousser le code sur GitHub
- ✅ Vérifier que le workflow CI se déclenche
- ✅ Vérifier que le job "test" passe sur les 3 versions de Python
- ✅ Documenter les résultats

### Pipeline CI - Flake8 et Trivy Scan (4 tâches)

#### Botan: Tâche 1 : Implémenter le step flake8 (premier run)
- ✅ Step "flake8" - Premier run dans le job "test" :
  - Commande : `flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics`
  - Exécuter sur le répertoire courant (`.`)
  - Compter le nombre d'erreurs
  - Sélectionner uniquement les erreurs E9, F63, F7, F82
  - Afficher le source des erreurs
  - Afficher les statistiques

#### Meryem: Tâche 2 : Implémenter le step flake8 (deuxième run)
- ✅ Step "flake8" - Deuxième run dans le job "test" :
  - Commande : `flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics`
  - Exécuter sur le répertoire courant (`.`)
  - Compter le nombre d'erreurs
  - Retourner "0" même avec des erreurs (`--exit-zero`)
  - Afficher les statistiques

### Résumé de l'implémentation actuelle du workflow CI

Le workflow `CI` est défini dans `.github/workflows/ci.yml` et contient :
- Un **job `test`** exécuté sur `ubuntu-latest` avec une **stratégie de matrice** pour Python `3.8`, `3.9` et `3.10`.
- Un step **`checkout`** (`actions/checkout@v5`) pour récupérer le code.
- Un step **`Python ${{ matrix.python-version }}`** (`actions/setup-python@v6`) pour installer la version de Python de la matrice.
- Un step **`dependencies`** qui met à jour `pip` et installe `flake8` et `pytest`.
- Un step **`flake8`** qui exécute deux runs :
  - 1er run : `flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics`
  - 2e run : `flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics`
- Un step **`pytest`** qui lance `pytest tests/` sur l'ensemble des tests du projet.

#### ✅ Aya : Tâche 3 : Implémenter le job "trivy-scan"
- ✅ Créer le job `trivy-scan` dans le workflow CI :
  - OS : `ubuntu-latest`
  - Step "checkout" avec `actions/checkout@v5`
  - Step "trivy FS mode" avec `aquasecurity/trivy-action@0.33.1`
    - Scan type : filesystem (`scan-type: 'fs'`)
    - Format : SARIF
    - Nom du fichier : `results.sarif`
    - Critères : `severity: 'CRITICAL,HIGH'`
  - Step "upload" avec `github/codeql-action/upload-sarif@v4`
    - Uploader le fichier `results.sarif`

#### Tâche 4 : Tester et valider les scans
- ✅ Vérifier que flake8 fonctionne correctement (2 runs)
- ✅ Vérifier que Trivy détecte les vulnérabilités dans le code
- Vérifier que le rapport SARIF est uploadé sur GitHub Security
- ✅ Vérifier l'affichage dans l'onglet Security du repository

### Pipeline CD et Documentation (4 tâches)

#### ✅ Meryem : Tâche 1 : Créer le workflow CD
- ✅ Créer le fichier `.github/workflows/cd.yml`
- ✅ Configurer le workflow :
  - Nom : "CD"
  - Trigger : `workflow_run` quand le workflow "CI" est complété
  - Condition : exécuter seulement si CI est réussi (`if: github.event.workflow_run.conclusion == 'success'`)
  - OS : `ubuntu-latest`

#### ✅ Aya :Tâche 2 : Implémenter le job "build" - Checkout et Login Docker
- ✅ Créer le job `build` dans le workflow CD :
  - OS : `ubuntu-latest`
  - Step "checkout" avec `actions/checkout@v5`
  - Step "login" avec `docker/login-action@v3`
    - Utiliser les secrets : 
      - `username: ${{ secrets.DOCKER_USERNAME }}`
      - `password: ${{ secrets.DOCKER_PASSWORD }}`

#### Tâche 3Meryem : Implémenter le step build and push Docker
- ✅Step "build and push" avec `docker/build-push-action@v6` :
  - ID : `id: push`
  - Context : répertoire courant (`.`)
  - Dockerfile : `Dockerfile` (celui fourni)
  - Push : `push: true`
  - Tags : `tags: username/xxx:latest` (remplacer par votre username Docker Hub)
  - Attention : le format doit être exactement `username/nom-image:latest`

#### Tâche 4 Botan: Documentation, secrets et tests finaux
- ✅ Configurer les secrets GitHub :
  - Aller dans Settings → Secrets and variables → Actions
  - Créer `DOCKER_USERNAME` : votre nom d'utilisateur Docker Hub
  - Créer `DOCKER_PASSWORD` : votre Personal Access Token Docker Hub (avec permissions Read & Write)
- ✅ Créer le fichier de soumission `.md` avec :
  - URL du repository GitHub public
  - Screenshot du pipeline CI qui passe (tous les jobs)
  - Screenshot du pipeline CD qui passe
  - Screenshot du repository Docker Hub montrant l'image poussée
  - Tous les fichiers créés (`.github/workflows/ci.yml` et `cd.yml`) en blocs de code
- ✅ Tester le pipeline complet end-to-end :
  - Push sur GitHub → CI se déclenche → CD se déclenche → Image sur Docker Hub

- Documentation disponible ici : [`Documentation.md`](./Documentation.md)


### Commandes de test utiles 

**Tester localement (si possible) :**
```bash
# Tester flake8
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Tester pytest
pytest tests/ -v
```

**Vérifier sur GitHub :**
- Onglet "Actions" : voir les workflows qui s'exécutent
- Onglet "Security" : voir les résultats de Trivy
- Docker Hub : vérifier que l'image est bien poussée


