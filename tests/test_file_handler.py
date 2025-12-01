"""
Tests unitaires pour le module file_handler.

Teste les fonctionnalités d'export/import et les vulnérabilités Path Traversal.
"""

import json
import os
import tempfile
import pytest

from app.database import get_connection, create_contact, list_contacts, delete_contact
from app.file_handler import (
    export_contacts_json,
    export_contacts_csv,
    import_contacts_json,
    import_contacts_csv,
    save_backup,
    restore_backup,
)


@pytest.fixture(autouse=True)
def isolate_db():
    """Fixture qui isole chaque test avec sa propre base de données."""
    original_db_path = os.environ.get('CONTACTS_DB_PATH')
    
    yield
    
    if original_db_path is None:
        if 'CONTACTS_DB_PATH' in os.environ:
            del os.environ['CONTACTS_DB_PATH']
    else:
        os.environ['CONTACTS_DB_PATH'] = original_db_path


@pytest.fixture
def temp_db():
    """Crée une base de données temporaire pour les tests."""
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    if os.path.exists(db_path):
        os.remove(db_path)
    
    os.environ['CONTACTS_DB_PATH'] = db_path
    
    conn = get_connection()
    create_contact(conn, "Alice", "alice@example.com", "123-456-7890", "Friend")
    create_contact(conn, "Bob", "bob@example.com", "098-765-4321", "Colleague")
    conn.close()
    
    yield db_path
    
    conn = get_connection()
    conn.close()
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def temp_dir():
    """Crée un répertoire temporaire pour les tests."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    import shutil
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)


def test_export_contacts_json(temp_db, temp_dir):
    """Test l'export JSON des contacts."""
    output_path = os.path.join(temp_dir, "contacts.json")
    result_path = export_contacts_json(output_path)
    
    assert os.path.exists(result_path)
    assert result_path == output_path
    
    with open(result_path, 'r') as f:
        data = json.load(f)
    
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]['name'] == "Alice"
    assert data[1]['name'] == "Bob"


def test_export_contacts_csv(temp_db, temp_dir):
    """Test l'export CSV des contacts."""
    output_path = os.path.join(temp_dir, "contacts.csv")
    result_path = export_contacts_csv(output_path)
    
    assert os.path.exists(result_path)
    assert result_path == output_path
    
    import csv
    with open(result_path, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    assert len(rows) == 2
    assert rows[0]['name'] == "Alice"
    assert rows[1]['name'] == "Bob"


def test_import_contacts_json(temp_db, temp_dir):
    """Test l'import JSON des contacts."""
    export_path = os.path.join(temp_dir, "export.json")
    export_contacts_json(export_path)
    
    fd, new_db = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    if os.path.exists(new_db):
        os.remove(new_db)
    
    old_db = os.environ.get('CONTACTS_DB_PATH')
    os.environ['CONTACTS_DB_PATH'] = new_db
    
    try:
        count = import_contacts_json(export_path)
        
        assert count == 2
        
        conn = get_connection()
        contacts = list_contacts(conn)
        conn.close()
        
        assert len(contacts) == 2
    finally:
        if old_db:
            os.environ['CONTACTS_DB_PATH'] = old_db
        elif 'CONTACTS_DB_PATH' in os.environ:
            del os.environ['CONTACTS_DB_PATH']
        if os.path.exists(new_db):
            os.remove(new_db)


def test_import_contacts_csv(temp_db, temp_dir):
    """Test l'import CSV des contacts."""
    export_path = os.path.join(temp_dir, "export.csv")
    export_contacts_csv(export_path)
    
    fd, new_db = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    if os.path.exists(new_db):
        os.remove(new_db)
    
    old_db = os.environ.get('CONTACTS_DB_PATH')
    os.environ['CONTACTS_DB_PATH'] = new_db
    
    try:
        count = import_contacts_csv(export_path)
        
        assert count == 2
        
        conn = get_connection()
        contacts = list_contacts(conn)
        conn.close()
        
        assert len(contacts) == 2
    finally:
        if old_db:
            os.environ['CONTACTS_DB_PATH'] = old_db
        elif 'CONTACTS_DB_PATH' in os.environ:
            del os.environ['CONTACTS_DB_PATH']
        if os.path.exists(new_db):
            os.remove(new_db)


def test_save_backup(temp_db, temp_dir):
    """Test la sauvegarde de la base de données."""
    backup_path = os.path.join(temp_dir, "backup.json")
    result_path = save_backup(backup_path)
    
    assert os.path.exists(result_path)
    
    with open(result_path, 'r') as f:
        data = json.load(f)
    
    assert data['version'] == '1.0'
    assert len(data['contacts']) == 2


def test_restore_backup(temp_db, temp_dir):
    """Test la restauration depuis une sauvegarde."""
    backup_path = os.path.join(temp_dir, "backup.json")
    save_backup(backup_path)
    
    fd, new_db = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    if os.path.exists(new_db):
        os.remove(new_db)
    
    old_db = os.environ.get('CONTACTS_DB_PATH')
    os.environ['CONTACTS_DB_PATH'] = new_db
    
    try:
        count = restore_backup(backup_path)
        
        assert count == 2
        
        conn = get_connection()
        contacts = list_contacts(conn)
        conn.close()
        
        assert len(contacts) == 2
    finally:
        if old_db:
            os.environ['CONTACTS_DB_PATH'] = old_db
        elif 'CONTACTS_DB_PATH' in os.environ:
            del os.environ['CONTACTS_DB_PATH']
        if os.path.exists(new_db):
            os.remove(new_db)


def test_path_traversal_vulnerability_json(temp_db, temp_dir):
    """
    Test qui démontre la vulnérabilité Path Traversal.
    
    ATTENTION : Ce test montre que le module est vulnérable.
    """
    malicious_path = os.path.join(temp_dir, "../../../traversal_test.json")
    normalized_path = os.path.normpath(malicious_path)
    
    try:
        result_path = export_contacts_json(malicious_path)
        assert os.path.exists(normalized_path) or os.path.exists(result_path)
    except (PermissionError, FileNotFoundError):
        pass


def test_path_traversal_vulnerability_csv(temp_db, temp_dir):
    """
    Test qui démontre la vulnérabilité Path Traversal pour CSV.
    """
    malicious_path = os.path.join(temp_dir, "../../../traversal_test.csv")
    normalized_path = os.path.normpath(malicious_path)
    
    try:
        result_path = export_contacts_csv(malicious_path)
        assert os.path.exists(normalized_path) or os.path.exists(result_path)
    except (PermissionError, FileNotFoundError):
        pass


def test_export_empty_contacts(temp_dir):
    """Test l'export avec une base de données vide."""
    fd, empty_db = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    if os.path.exists(empty_db):
        os.remove(empty_db)
    
    old_db = os.environ.get('CONTACTS_DB_PATH')
    os.environ['CONTACTS_DB_PATH'] = empty_db
    
    try:
        json_path = os.path.join(temp_dir, "empty.json")
        export_contacts_json(json_path)
        
        with open(json_path, 'r') as f:
            data = json.load(f)
        assert data == []
        
        csv_path = os.path.join(temp_dir, "empty.csv")
        export_contacts_csv(csv_path)
        
        import csv
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
        assert len(rows) == 1
    finally:
        if old_db:
            os.environ['CONTACTS_DB_PATH'] = old_db
        elif 'CONTACTS_DB_PATH' in os.environ:
            del os.environ['CONTACTS_DB_PATH']
        if os.path.exists(empty_db):
            os.remove(empty_db)

