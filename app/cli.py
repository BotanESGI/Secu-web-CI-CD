"""
Interface CLI principale pour la gestion des contacts.

Ce module utilise la base de données et la gestion de fichiers.
Il contient aussi un export HTML volontairement vulnérable à la XSS.
"""

from app import database
from app import file_handler


def main_menu() -> None:
    """Affiche le menu principal et gère les choix de l'utilisateur."""
    while True:
        print("\n=== Gestion de contacts ===")
        print("1. Ajouter un contact")
        print("2. Lister les contacts")
        print("3. Rechercher un contact")
        print("4. Modifier un contact")
        print("5. Supprimer un contact")
        print("6. Exporter les contacts")
        print("7. Importer des contacts")
        print("8. Sauvegarde / Restauration")
        print("0. Quitter")

        choice = input("Votre choix: ").strip()

        if choice == "1":
            handle_add_contact()
        elif choice == "2":
            handle_list_contacts()
        elif choice == "3":
            handle_search_contacts()
        elif choice == "4":
            handle_update_contact()
        elif choice == "5":
            handle_delete_contact()
        elif choice == "6":
            handle_export_menu()
        elif choice == "7":
            handle_import_menu()
        elif choice == "8":
            handle_backup_menu()
        elif choice == "0":
            print("Au revoir.")
            break
        else:
            print("Choix invalide.")


def handle_add_contact() -> None:
    """Ajoute un nouveau contact."""
    print("\n=== Ajouter un contact ===")
    name = input("Nom: ")
    email = input("Email: ")
    phone = input("Téléphone: ")
    notes = input("Notes: ")

    conn = database.get_connection()
    contact_id = database.create_contact(conn, name, email, phone, notes)
    conn.close()

    print(f"Contact créé avec l'id {contact_id}.")


def handle_list_contacts() -> None:
    """Affiche tous les contacts."""
    print("\n=== Liste des contacts ===")
    conn = database.get_connection()
    contacts = database.list_contacts(conn)
    conn.close()

    if not contacts:
        print("Aucun contact.")
        return

    for c in contacts:
        print(f"[{c['id']}] {c['name']} - {c['email']} - {c['phone']} - {c['notes']}")


def handle_search_contacts() -> None:
    """Recherche des contacts par mot-clé (SQLi possible dans database.search_contacts)."""
    print("\n=== Rechercher un contact ===")
    query = input("Mot-clé: ")

    conn = database.get_connection()
    results = database.search_contacts(conn, query)
    conn.close()

    if not results:
        print("Aucun résultat.")
        return

    for c in results:
        print(f"[{c['id']}] {c['name']} - {c['email']} - {c['phone']} - {c['notes']}")


def handle_update_contact() -> None:
    """Modifie un contact existant."""
    print("\n=== Modifier un contact ===")
    contact_id = input("ID du contact à modifier: ").strip()
    if not contact_id.isdigit():
        print("ID invalide.")
        return

    name = input("Nouveau nom (laisser vide pour ne pas changer): ")
    email = input("Nouvel email (laisser vide pour ne pas changer): ")
    phone = input("Nouveau téléphone (laisser vide pour ne pas changer): ")
    notes = input("Nouvelles notes (laisser vide pour ne pas changer): ")

    kwargs = {}
    if name:
        kwargs["name"] = name
    if email:
        kwargs["email"] = email
    if phone:
        kwargs["phone"] = phone
    if notes:
        kwargs["notes"] = notes

    if not kwargs:
        print("Rien à modifier.")
        return

    conn = database.get_connection()
    database.update_contact(conn, int(contact_id), **kwargs)
    conn.close()

    print("Contact mis à jour.")


def handle_delete_contact() -> None:
    """Supprime un contact."""
    print("\n=== Supprimer un contact ===")
    contact_id = input("ID du contact à supprimer: ").strip()
    if not contact_id.isdigit():
        print("ID invalide.")
        return

    conn = database.get_connection()
    database.delete_contact(conn, int(contact_id))
    conn.close()

    print("Contact supprimé.")


def handle_export_menu() -> None:
    """Menu d'export des contacts."""
    print("\n=== Export des contacts ===")
    print("1. Export JSON")
    print("2. Export CSV")
    print("3. Export HTML (XSS possible)")
    choice = input("Votre choix: ").strip()

    path = input("Chemin de fichier de sortie: ").strip()

    if choice == "1":
        result = file_handler.export_contacts_json(path)
        print(f"Contacts exportés en JSON dans {result}.")
    elif choice == "2":
        result = file_handler.export_contacts_csv(path)
        print(f"Contacts exportés en CSV dans {result}.")
    elif choice == "3":
        result = export_contacts_html(path)
        print(f"Contacts exportés en HTML dans {result}.")
    else:
        print("Choix invalide.")


def handle_import_menu() -> None:
    """Menu d'import des contacts."""
    print("\n=== Import des contacts ===")
    print("1. Import JSON")
    print("2. Import CSV")
    choice = input("Votre choix: ").strip()

    path = input("Chemin du fichier à importer: ").strip()

    if choice == "1":
        count = file_handler.import_contacts_json(path)
        print(f"{count} contacts importés depuis le JSON.")
    elif choice == "2":
        count = file_handler.import_contacts_csv(path)
        print(f"{count} contacts importés depuis le CSV.")
    else:
        print("Choix invalide.")


def handle_backup_menu() -> None:
    """Menu pour la sauvegarde et la restauration."""
    print("\n=== Sauvegarde / Restauration ===")
    print("1. Sauvegarder")
    print("2. Restaurer")
    choice = input("Votre choix: ").strip()

    path = input("Chemin du fichier de sauvegarde: ").strip()

    if choice == "1":
        result = file_handler.save_backup(path)
        print(f"Sauvegarde créée dans {result}.")
    elif choice == "2":
        count = file_handler.restore_backup(path)
        print(f"{count} contacts restaurés.")
    else:
        print("Choix invalide.")


def export_contacts_html(output_path: str) -> str:
    """
    Exporte les contacts en HTML.

    VULNÉRABILITÉ XSS : les données ne sont pas échappées avant d'être
    affichées dans le fichier HTML.
    """
    conn = database.get_connection()
    contacts = database.list_contacts(conn)
    conn.close()

    html_parts = []
    html_parts.append("<html><head><title>Contacts</title></head><body>")
    html_parts.append("<h1>Liste des contacts</h1>")
    html_parts.append("<table border='1'>")
    html_parts.append(
        "<tr><th>ID</th><th>Nom</th><th>Email</th>"
        "<th>Téléphone</th><th>Notes</th></tr>"
    )

    for c in contacts:
        # Les valeurs sont injectées directement : XSS possible.
        html_parts.append(
            f"<tr>"
            f"<td>{c['id']}</td>"
            f"<td>{c['name']}</td>"
            f"<td>{c['email']}</td>"
            f"<td>{c['phone']}</td>"
            f"<td>{c['notes']}</td>"
            f"</tr>"
        )

    html_parts.append("</table>")
    html_parts.append("</body></html>")

    html_content = "\n".join(html_parts)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return output_path


__all__ = [
    "main_menu",
    "handle_add_contact",
    "handle_list_contacts",
    "handle_search_contacts",
    "handle_update_contact",
    "handle_delete_contact",
    "handle_export_menu",
    "handle_import_menu",
    "handle_backup_menu",
    "export_contacts_html",
]


if __name__ == "__main__":
    main_menu()


