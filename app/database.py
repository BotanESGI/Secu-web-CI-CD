"""
Module de gestion de la base de données SQLite pour les contacts.

Module est volontairement vulnérable à l'injection SQL
(requêtes non paramétrées, concaténation de chaînes).
"""

import os
import sqlite3
from typing import Any, Dict, List, Optional

DEFAULT_DB_PATH = "contacts.db"


def get_connection(db_path: str = None) -> sqlite3.Connection:
    """
    Retourne une connexion SQLite vers la base de données.
    Crée la base et la table si nécessaire.
    
    Si db_path n'est pas fourni, utilise CONTACTS_DB_PATH de l'environnement
    ou "contacts.db" par défaut.
    """
    if db_path is None:
        db_path = os.environ.get("CONTACTS_DB_PATH", DEFAULT_DB_PATH)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    _init_schema(conn)
    return conn


def _init_schema(conn: sqlite3.Connection) -> None:
    """
    Crée la table contacts si elle n'existe pas.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            notes TEXT
        )
        """
    )
    conn.commit()


def create_contact(conn: sqlite3.Connection, name: str, email: str, phone: str = "", notes: str = "") -> int:
    """
    Crée un contact.

    VULNÉRABILITÉ : utilisation de f-strings / formatage de chaînes
    sans paramètres préparés.
    """
    cursor = conn.cursor()

   
    safe_name = name.replace("'", "''")
    safe_email = email.replace("'", "''")
    safe_phone = phone.replace("'", "''")
    safe_notes = notes.replace("'", "''")

    query = (
        f"INSERT INTO contacts (name, email, phone, notes) "
        f"VALUES ('{safe_name}', '{safe_email}', '{safe_phone}', '{safe_notes}')"
    )
    cursor.execute(query)
    conn.commit()
    return cursor.lastrowid


def get_contact(conn: sqlite3.Connection, contact_id: int) -> Optional[Dict[str, Any]]:
    """
    Récupère un contact par son id.

    VULNÉRABILITÉ : interpolation directe de l'id dans la requête.
    """
    cursor = conn.cursor()
    query = f"SELECT id, name, email, phone, notes FROM contacts WHERE id = {contact_id}"
    cursor.execute(query)
    row = cursor.fetchone()
    if row is None:
        return None
    return dict(row)


def list_contacts(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """
    Liste tous les contacts.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, phone, notes FROM contacts ORDER BY id ASC")
    rows = cursor.fetchall()
    return [dict(r) for r in rows]


def update_contact(
    conn: sqlite3.Connection,
    contact_id: int,
    name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    notes: Optional[str] = None,
) -> None:
    """
    Met à jour un contact.

    VULNÉRABILITÉ : construction de la requête au moyen de concaténations
    de chaînes non sécurisées.
    """
    cursor = conn.cursor()
    updates = []
    if name is not None:
        updates.append(f"name = '{name}'")
    if email is not None:
        updates.append(f"email = '{email}'")
    if phone is not None:
        updates.append(f"phone = '{phone}'")
    if notes is not None:
        updates.append(f"notes = '{notes}'")

    if not updates:
        return

    set_clause = ", ".join(updates)
    query = f"UPDATE contacts SET {set_clause} WHERE id = {contact_id}"
    cursor.execute(query)
    conn.commit()


def delete_contact(conn: sqlite3.Connection, contact_id: int) -> None:
    """
    Supprime un contact.

    VULNÉRABILITÉ : interpolation directe de l'id.
    """
    cursor = conn.cursor()
    query = f"DELETE FROM contacts WHERE id = {contact_id}"
    cursor.execute(query)
    conn.commit()


def search_contacts(conn: sqlite3.Connection, query_string: str) -> List[Dict[str, Any]]:
    """
    Recherche de contacts sur les champs name, email et notes.

    VULNÉRABILITÉ SQLi : le terme de recherche est injecté directement dans
    la requête sans échappement ni paramètres préparés.
    Exemple d'abus : "' OR 1=1 --"
    """
    cursor = conn.cursor()
    query = (
        "SELECT id, name, email, phone, notes FROM contacts "
        f"WHERE name LIKE '%{query_string}%' "
        f"   OR email LIKE '%{query_string}%' "
        f"   OR notes LIKE '%{query_string}%' "
        "ORDER BY id ASC"
    )
    cursor.execute(query)
    rows = cursor.fetchall()
    return [dict(r) for r in rows]


__all__ = [
    "get_connection",
    "create_contact",
    "get_contact",
    "list_contacts",
    "update_contact",
    "delete_contact",
    "search_contacts",
]


