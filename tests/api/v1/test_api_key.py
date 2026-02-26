from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.models.device import Device


def is_valid_uuid(value: str, version: int = 4) -> bool:
    try:
        uuid_obj = UUID(value, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == value


class TestApiKey:

    @pytest.mark.asyncio
    async def test_create_api_key(
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

    @pytest.mark.asyncio
    async def test_create_api_key_not_admin(
        self, client: TestClient, admin_headers: dict, default_devices: list[Device]
    ):
        """Creating an API key should return 403 if the user is not an admin."""
        response = client.post(
            f"/api/v1/keys/{default_devices[0].id}",
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_api_key_invalid_device(
        self, client: TestClient, admin_headers: dict
    ):
        """Creating an API key should return 404 if the device does not exist."""
        response = client.post(
            "/api/v1/keys/00000000-0000-0000-0000-000000000000",
            headers=admin_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_revoke_api_key(
        self, client: TestClient, admin_headers: dict, default_devices: list[Device]
    ):
        """Revoking an API key should return 200 and the revoked status."""
        response = client.post(
            f"/api/v1/keys/{default_devices[0].id}",
            headers=admin_headers,
        )
        admin_headers["X-API-Key"] = response.json().get("api_key")
        admin_headers["X-Device-Id"] = str(default_devices[0].id)
        revoked = client.put(
            "/api/v1/keys",
            headers=admin_headers,
        )
        data = revoked.json()
        assert data.get("message", "") == "API key revoked successfully"

    @pytest.mark.asyncio
    async def test_revoke_api_key_incorrect_key(
        self, client: TestClient, admin_headers: dict, default_devices: list[Device]
    ):
        """Revoking an API key should return 403"""
        _ = client.post(
            f"/api/v1/keys/{default_devices[0].id}",
            headers=admin_headers,
        )
        admin_headers["X-API-Key"] = "00000000-0000-0000-0000-000000000000"
        admin_headers["X-Device-Id"] = str(default_devices[0].id)
        revoked = client.put(
            "/api/v1/keys",
            headers=admin_headers,
        )
        assert revoked.status_code == 401

    @pytest.mark.asyncio
    async def test_revoke_api_key_non_admin(
        self, client: TestClient, admin_headers: dict, default_devices: list[Device]
    ):
        """Revoking an API key should return 403."""
        response = client.post(
            f"/api/v1/keys/{default_devices[0].id}",
            headers=admin_headers,
        )
        admin_headers["X-API-Key"] = response.json().get("api_key")
        admin_headers["X-Device-Id"] = str(default_devices[0].id)
        revoked = client.put(
            "/api/v1/keys",
        )
        assert revoked.status_code == 403

    @pytest.mark.asyncio
    async def test_refresh_api_key(
        self, client: TestClient, admin_headers: dict, default_devices: list[Device]
    ):
        """Creating an API key should return 201 and the API key data."""
        response = client.post(
            f"/api/v1/keys/{default_devices[0].id}",
            headers=admin_headers,
        )
        assert response.status_code == 201
        new_response = client.put(
            f"/api/v1/keys/refresh/{default_devices[0].id}",
            headers=admin_headers,
        )
        assert new_response.status_code == 200
        data = new_response.json()
        assert "id" in data
        assert "api_key" in data

    @pytest.mark.asyncio
    async def test_refresh_api_key_non_admin(
        self, client: TestClient, admin_headers: dict, default_devices: list[Device]
    ):
        """Creating an API key should return 201 and the API key data."""
        response = client.post(
            f"/api/v1/keys/{default_devices[0].id}",
            headers=admin_headers,
        )
        assert response.status_code == 201
        new_response = client.put(
            f"/api/v1/keys/refresh/{default_devices[0].id}",
        )
        assert new_response.status_code == 403
