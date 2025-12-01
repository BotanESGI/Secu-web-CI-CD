import os
import sqlite3

import pytest

from app import database


TEST_DB_PATH = "test_contacts.db"


@pytest.fixture(autouse=True)
def clean_test_db():
    """
    Fixture qui s'assure que la base de test est propre avant chaque test.
    """
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    conn = database.get_connection(TEST_DB_PATH)
    yield conn
    conn.close()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


def test_create_and_get_contact(clean_test_db: sqlite3.Connection):
    conn = clean_test_db
    contact_id = database.create_contact(
        conn,
        name="Alice",
        email="alice@example.com",
        phone="0123456789",
        notes="Amie d'enfance",
    )

    contact = database.get_contact(conn, contact_id)
    assert contact is not None
    assert contact["name"] == "Alice"
    assert contact["email"] == "alice@example.com"


def test_list_contacts_returns_all(clean_test_db: sqlite3.Connection):
    conn = clean_test_db
    database.create_contact(conn, "Alice", "alice@example.com")
    database.create_contact(conn, "Bob", "bob@example.com")

    contacts = database.list_contacts(conn)
    assert len(contacts) == 2
    names = {c["name"] for c in contacts}
    assert names == {"Alice", "Bob"}


def test_update_contact_changes_fields(clean_test_db: sqlite3.Connection):
    conn = clean_test_db
    contact_id = database.create_contact(conn, "Alice", "alice@example.com")

    database.update_contact(conn, contact_id, name="Alice updated", phone="999")
    contact = database.get_contact(conn, contact_id)

    assert contact is not None
    assert contact["name"] == "Alice updated"
    assert contact["phone"] == "999"


def test_delete_contact_removes_entry(clean_test_db: sqlite3.Connection):
    conn = clean_test_db
    contact_id = database.create_contact(conn, "Alice", "alice@example.com")

    database.delete_contact(conn, contact_id)
    contact = database.get_contact(conn, contact_id)

    assert contact is None


def test_search_contacts_basic(clean_test_db: sqlite3.Connection):
    """
    Test simple de la recherche (sans exploiter la vulnérabilité).
    """
    conn = clean_test_db
    database.create_contact(conn, "Alice", "alice@example.com", notes="Paris")
    database.create_contact(conn, "Bob", "bob@example.com", notes="Lyon")

    results = database.search_contacts(conn, "Paris")
    assert len(results) == 1
    assert results[0]["name"] == "Alice"



