"""
Tests principaux pour l'interface CLI.

On teste ici surtout la fonction d'export HTML et quelques
fonctions utilitaires sans interaction utilisateur directe.
"""

import os
import tempfile

from app import database
from app import cli


def test_export_contacts_html_cree_fichier_et_contenu():
    """Vérifie que l'export HTML crée un fichier avec les contacts."""
    # Prépare une base temporaire avec un contact
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    if os.path.exists(db_path):
        os.remove(db_path)

    old_db = os.environ.get("CONTACTS_DB_PATH")
    os.environ["CONTACTS_DB_PATH"] = db_path

    try:
        conn = database.get_connection()
        database.create_contact(
            conn,
            name="Alice",
            email="alice@example.com",
            phone="0123456789",
            notes="<script>alert('xss')</script>",
        )
        conn.close()

        # Fichier HTML temporaire
        fd_html, html_path = tempfile.mkstemp(suffix=".html")
        os.close(fd_html)
        if os.path.exists(html_path):
            os.remove(html_path)

        # Appel de la fonction d'export
        result_path = cli.export_contacts_html(html_path)

        assert os.path.exists(result_path)

        with open(result_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Le nom et les notes du contact doivent apparaître dans le HTML
        assert "Alice" in content
        assert "<script>alert('xss')</script>" in content
    finally:
        # Nettoyage
        if old_db:
            os.environ["CONTACTS_DB_PATH"] = old_db
        elif "CONTACTS_DB_PATH" in os.environ:
            del os.environ["CONTACTS_DB_PATH"]

        if os.path.exists(db_path):
            os.remove(db_path)

        if os.path.exists(html_path):
            os.remove(html_path)


def test_handle_list_contacts_ne_crashe_pas_sans_contact(capsys):
    """Vérifie que handle_list_contacts fonctionne même si la base est vide."""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    if os.path.exists(db_path):
        os.remove(db_path)

    old_db = os.environ.get("CONTACTS_DB_PATH")
    os.environ["CONTACTS_DB_PATH"] = db_path

    try:
        # Appel direct : la base est vide mais la fonction ne doit pas planter
        cli.handle_list_contacts()
        captured = capsys.readouterr()
        # On s'assure juste qu'un message a été affiché
        assert "Aucun contact" in captured.out
    finally:
        if old_db:
            os.environ["CONTACTS_DB_PATH"] = old_db
        elif "CONTACTS_DB_PATH" in os.environ:
            del os.environ["CONTACTS_DB_PATH"]

        if os.path.exists(db_path):
            os.remove(db_path)


