from uuid import UUID

from fastapi.testclient import TestClient

from app.models.device import Device


def is_valid_uuid(value: str, version: int = 4) -> bool:
    try:
        uuid_obj = UUID(value, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == value


class TestApiKey:

    def test_create_api_key(
        self, client: TestClient, admin_headers: dict, default_devices: list[Device]
    ):
        """Creating an API key should return 201 and the API key data."""
        response = client.post(
            f"/api/v1/keys/{default_devices[0].id}",
            headers=admin_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert is_valid_uuid(data.get("id", ""))

    def test_create_api_key_not_admin(
        self, client: TestClient, default_devices: list[Device]
    ):
        """Creating an API key without admin credentials should return 403."""
        response = client.post(
            f"/api/v1/keys/{default_devices[0].id}",
        )
        assert response.status_code == 403

    def test_create_api_key_invalid_device(
        self, client: TestClient, admin_headers: dict
    ):
        """Creating an API key for a non-existent device should return 404."""
        response = client.post(
            "/api/v1/keys/00000000-0000-0000-0000-000000000000",
            headers=admin_headers,
        )
        assert response.status_code == 404

    def test_revoke_api_key(
        self, client: TestClient, admin_headers: dict, default_devices: list[Device]
    ):
        """Revoking an API key should return 200 and a confirmation message."""
        client.post(
            f"/api/v1/keys/{default_devices[0].id}",
            headers=admin_headers,
        )
        response = client.patch(
            f"/api/v1/keys/{default_devices[0].id}/revoke",
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json().get("message") == "API key revoked successfully"

    def test_revoke_api_key_not_found(self, client: TestClient, admin_headers: dict):
        """Revoking an API key for a non-existent device should return 404."""
        response = client.patch(
            "/api/v1/keys/00000000-0000-0000-0000-000000000000/revoke",
            headers=admin_headers,
        )
        assert response.status_code == 404

    def test_revoke_api_key_non_admin(
        self, client: TestClient, default_devices: list[Device]
    ):
        """Revoking an API key without admin credentials should return 403."""
        response = client.patch(
            f"/api/v1/keys/{default_devices[0].id}/revoke",
        )
        assert response.status_code == 403

    def test_refresh_api_key(
        self, client: TestClient, admin_headers: dict, default_devices: list[Device]
    ):
        """Refreshing an API key should return 200 and new key data."""
        client.post(
            f"/api/v1/keys/{default_devices[0].id}",
            headers=admin_headers,
        )
        response = client.post(
            f"/api/v1/keys/{default_devices[0].id}/refresh",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "api_key" in data

    def test_refresh_api_key_non_admin(
        self, client: TestClient, admin_headers: dict, default_devices: list[Device]
    ):
        """Refreshing an API key without admin credentials should return 403."""
        client.post(
            f"/api/v1/keys/{default_devices[0].id}",
            headers=admin_headers,
        )
        response = client.post(
            f"/api/v1/keys/{default_devices[0].id}/refresh",
        )
        assert response.status_code == 403

    def test_create_duplicate_api_key(
        self, client: TestClient, admin_headers: dict, default_devices: list[Device]
    ):
        """Creating a second API key for the same device should return 409."""
        client.post(
            f"/api/v1/keys/{default_devices[0].id}",
            headers=admin_headers,
        )
        response = client.post(
            f"/api/v1/keys/{default_devices[0].id}",
            headers=admin_headers,
        )
        assert response.status_code == 409

    def test_refresh_revoked_api_key(
        self, client: TestClient, admin_headers: dict, default_devices: list[Device]
    ):
        """Refreshing a revoked API key should unrevoke it and allow data submission."""
        create_response = client.post(
            f"/api/v1/keys/{default_devices[0].id}",
            headers=admin_headers,
        )
        client.patch(
            f"/api/v1/keys/{default_devices[0].id}/revoke",
            headers=admin_headers,
        )
        refresh_response = client.post(
            f"/api/v1/keys/{default_devices[0].id}/refresh",
            headers=admin_headers,
        )
        assert refresh_response.status_code == 200
        new_key = refresh_response.json().get("api_key")
        assert new_key != create_response.json().get("api_key")

        data_response = client.post(
            "/api/v1/data/",
            json={"temperature": 22.5},
            headers={
                "X-API-Key": new_key,
                "X-Device-Id": str(default_devices[0].id),
            },
        )
        assert data_response.status_code == 201
