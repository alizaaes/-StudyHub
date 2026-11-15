
import os
import tempfile

import pytest

# Keep the database created during app startup outside the project.
os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="studyhub-test-bootstrap-")

from app import app as flask_app
import database as dt


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Give every test its own temporary database.
    test_db = tmp_path / "test_students.db"
    monkeypatch.setattr(dt, "DATABASE_NAME", str(test_db))

    # Create the tables in the temporary database.
    dt.create_database()

    flask_app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key"
    )

    with flask_app.test_client() as test_client:
        yield test_client
