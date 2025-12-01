"""
Module de gestion des fichiers pour l'export/import de contacts.

Ce module est volontairement vulnérable au Path Traversal
(validation insuffisante des chemins de fichiers).
"""

import csv
import json
import os
from typing import Any, Dict, List

from app.database import get_connection, list_contacts, create_contact


DEFAULT_EXPORT_DIR = "data/exports"


def export_contacts_json(output_path: str) -> str:
    """
    Exporte tous les contacts au format JSON.

    VULNÉRABILITÉ Path Traversal : le chemin n'est pas validé,
    permet d'écrire n'importe où sur le système.
    Exemple d'abus : "../../../etc/passwd"
    """
    conn = get_connection()
    contacts = list_contacts(conn)
    conn.close()

   
    full_path = output_path

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)

    return full_path


def export_contacts_csv(output_path: str) -> str:
    """
    Exporte tous les contacts au format CSV.

    VULNÉRABILITÉ Path Traversal : le chemin n'est pas validé.
    """
    conn = get_connection()
    contacts = list_contacts(conn)
    conn.close()

    full_path = output_path

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    if contacts:
        fieldnames = ['id', 'name', 'email', 'phone', 'notes']
        with open(full_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(contacts)
    else:
        with open(full_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'email', 'phone', 'notes'])

    return full_path


def import_contacts_json(input_path: str) -> int:
    """
    Importe des contacts depuis un fichier JSON.

    VULNÉRABILITÉ Path Traversal : le chemin n'est pas validé,
    permet de lire n'importe quel fichier du système.
    Exemple d'abus : "../../../etc/passwd"
    """
    
    full_path = input_path

    with open(full_path, 'r', encoding='utf-8') as f:
        contacts = json.load(f)

    conn = get_connection()
    count = 0
    for contact in contacts:
        name = contact.get('name', '')
        email = contact.get('email', '')
        phone = contact.get('phone', '')
        notes = contact.get('notes', '')
        create_contact(conn, name, email, phone, notes)
        count += 1
    conn.close()

    return count


def import_contacts_csv(input_path: str) -> int:
    """
    Importe des contacts depuis un fichier CSV.

    VULNÉRABILITÉ Path Traversal : le chemin n'est pas validé.
    """
    full_path = input_path

    conn = get_connection()
    count = 0

    with open(full_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get('name', '')
            email = row.get('email', '')
            phone = row.get('phone', '')
            notes = row.get('notes', '')
            create_contact(conn, name, email, phone, notes)
            count += 1
    conn.close()

    return count


def save_backup(backup_path: str) -> str:
    """
    Sauvegarde la base de données complète dans un fichier JSON.

    VULNÉRABILITÉ Path Traversal : permet d'écrire n'importe où.
    """
    conn = get_connection()
    contacts = list_contacts(conn)
    conn.close()

    full_path = backup_path

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    backup_data = {
        'version': '1.0',
        'contacts': contacts
    }

    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)

    return full_path


def restore_backup(backup_path: str) -> int:
    """
    Restaure la base de données depuis un fichier de sauvegarde.

    VULNÉRABILITÉ Path Traversal : permet de lire n'importe quel fichier.
    """
    full_path = backup_path

    with open(full_path, 'r', encoding='utf-8') as f:
        backup_data = json.load(f)

    contacts = backup_data.get('contacts', [])

    conn = get_connection()
    count = 0
    for contact in contacts:
        name = contact.get('name', '')
        email = contact.get('email', '')
        phone = contact.get('phone', '')
        notes = contact.get('notes', '')
        create_contact(conn, name, email, phone, notes)
        count += 1
    conn.close()

    return count


__all__ = [
    "export_contacts_json",
    "export_contacts_csv",
    "import_contacts_json",
    "import_contacts_csv",
    "save_backup",
    "restore_backup",
]

