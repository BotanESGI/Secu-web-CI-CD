"""
Module de configuration avec secrets en dur.

VULNÉRABILITÉ : Tous les secrets sont stockés directement dans le code,
ce qui est une mauvaise pratique de sécurité.
"""


API_TOKEN = "sk_live_51H3ll0W0rld_4bCdEfGhIjKlMnOpQrStUvWxYz"
API_SECRET_KEY = "secret_key_12345_never_commit_this"

DB_PASSWORD = "SuperSecretPassword123!"
DB_USER = "admin"

ENCRYPTION_KEY = "my_secret_encryption_key_do_not_share"

JWT_SECRET = "jwt_secret_key_very_secure_not"

AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

ADMIN_PASSWORD = "admin123"

GITHUB_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"

APP_NAME = "Contact Manager"
APP_VERSION = "1.0.0"
DEBUG_MODE = True

DEFAULT_EXPORT_DIR = "data/exports"

__all__ = [
    "API_TOKEN",
    "API_SECRET_KEY",
    "DB_PASSWORD",
    "DB_USER",
    "ENCRYPTION_KEY",
    "JWT_SECRET",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "ADMIN_PASSWORD",
    "GITHUB_TOKEN",
    "APP_NAME",
    "APP_VERSION",
    "DEBUG_MODE",
    "DEFAULT_EXPORT_DIR",
]

