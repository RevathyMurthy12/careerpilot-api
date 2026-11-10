
import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Safety check: stop immediately if the tests would use PostgreSQL
    assert main.DATABASE_URL is None, "DATABASE_URL must not be set during tests"

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


# ----- Characterisation tests: record current behaviour before refactoring -----


def test_put_missing_application_returns_404_and_creates_no_row(client):
    response = client.put(
        "/applications/99999",
        json={"company": "XYZ", "role": "Developer", "status": "Interview"}
    )

    assert response.status_code == 404
    assert client.get("/applications").json() == []


def test_missing_application_404_detail_message(client):
    put_response = client.put(
        "/applications/99999",
        json={"company": "XYZ", "role": "Developer"}
    )
    delete_response = client.delete("/applications/99999")

    assert put_response.json() == {"detail": "Application not found"}
    assert delete_response.json() == {"detail": "Application not found"}


def test_default_status_is_applied(client):
    response = client.post(
        "/applications",
        json={"company": "Google", "role": "Developer"}
    )

    assert response.status_code == 201
    assert response.json()["application"]["status"] == "Applied"


@pytest.mark.parametrize(
    "payload",
    [
        {"company": "", "role": "Developer"},          # empty company
        {"company": "   ", "role": "Developer"},       # whitespace-only company
        {"company": "Google", "role": "x" * 101},      # role over 100 characters
        {"role": "Developer"},                         # missing company
    ],
)
def test_invalid_application_is_rejected_and_not_saved(client, payload):
    response = client.post("/applications", json=payload)

    assert response.status_code == 422
    assert client.get("/applications").json() == []


def test_whitespace_is_stripped_from_company_and_role(client):
    response = client.post(
        "/applications",
        json={"company": "  Google  ", "role": "  Python Developer "}
    )

    application = response.json()["application"]
    assert application["company"] == "Google"
    assert application["role"] == "Python Developer"


def test_response_messages_and_delete_id(client):
    created = client.post(
        "/applications",
        json={"company": "ABC", "role": "Developer"}
    )
    assert created.json()["message"] == "Application created successfully"
    application_id = created.json()["application"]["id"]

    updated = client.put(
        f"/applications/{application_id}",
        json={"company": "XYZ", "role": "Developer", "status": "Interview"}
    )
    assert updated.json()["message"] == "Application updated successfully"

    deleted = client.delete(f"/applications/{application_id}")
    assert deleted.json() == {
        "message": "Application deleted successfully",
        "id": application_id,
    }
