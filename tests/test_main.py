
import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Use a separate temporary database for testing
    test_database = tmp_path / "test.db"
    monkeypatch.setattr(main, "DATABASE", str(test_database))
    main.create_table()

    with TestClient(main.app) as test_client:
        yield test_client


def test_create_and_read_application(client):
    response = client.post(
        "/applications",
        json={
            "company": "Google",
            "role": "Python Developer",
            "status": "Applied"
        }
    )

    assert response.status_code == 201
    application_id = response.json()["application"]["id"]

    response = client.get("/applications")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == application_id


def test_update_application(client):
    created = client.post(
        "/applications",
        json={"company": "ABC", "role": "Developer"}
    )
    application_id = created.json()["application"]["id"]

    response = client.put(
        f"/applications/{application_id}",
        json={
            "company": "XYZ",
            "role": "Python Developer",
            "status": "Interview"
        }
    )

    assert response.status_code == 200
    assert response.json()["application"]["company"] == "XYZ"
    assert response.json()["application"]["status"] == "Interview"


def test_delete_application(client):
    created = client.post(
        "/applications",
        json={"company": "ABC", "role": "Developer"}
    )
    application_id = created.json()["application"]["id"]

    response = client.delete(f"/applications/{application_id}")

    assert response.status_code == 200

    applications = client.get("/applications").json()
    assert applications == []


def test_invalid_status_is_rejected(client):
    response = client.post(
        "/applications",
        json={
            "company": "Google",
            "role": "Developer",
            "status": "Maybe"
        }
    )

    assert response.status_code == 422


def test_missing_application_returns_404(client):
    response = client.delete("/applications/99999")

    assert response.status_code == 404
