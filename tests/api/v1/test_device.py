from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.models.device import Device


class TestDevice:

    @pytest.mark.asyncio
    async def test_create_device(self, client: TestClient, admin_headers: dict):
        """Creating a device should return 201 and the device data."""
        payload = {
            "name": "Test Device",
            "description": "A device for testing",
        }
        response = client.post(
            "/api/v1/devices/",
            headers=admin_headers,
            json=payload,
        )
        assert response.status_code == 201
        data = response.json()
        assert data.get("name", "") == payload.get("name", "")
        assert data.get("description", "") == payload.get("description", "")

    @pytest.mark.asyncio
    async def test_create_device_non_admin(self, client: TestClient):
        """Creating a device should return 201 and the device data."""
        payload = {
            "name": "Test Device non-admin",
            "description": "A device for testing",
        }
        response = client.post(
            "/api/v1/devices/",
            json=payload,
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_read_device_by_id(
        self, client: TestClient, admin_headers: dict, default_devices: list[Device]
    ):
        """Getting devices should return 200 and a list of devices."""
        response = client.get(
            f"/api/v1/devices/{default_devices[0].id}",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("name", "") == default_devices[0].name
        assert data.get("description", "") == default_devices[0].description
        assert data.get("notes", "") == default_devices[0].notes

    @pytest.mark.asyncio
    async def test_update_device(
        self, client: TestClient, admin_headers: dict, default_devices: list[Device]
    ):
        """Updating a device should return 200 and the updated device data."""
        payload = {
            "name": "Updated Device Name",
            "description": "Updated description",
            "notes": {"updated": True},
        }
        response = client.put(
            f"/api/v1/devices/{default_devices[2].id}",
            headers=admin_headers,
            json=payload,
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("name", "") == payload.get("name", "")
        assert data.get("description", "") == payload.get("description", "")
        assert data.get("notes", {}) == payload.get("notes", {})

    @pytest.mark.asyncio
    async def test_delete_device(
        self, client: TestClient, admin_headers: dict, default_devices: list[Device]
    ):
        """Deleting a device should return 204 and the device should no longer be retrievable."""
        response = client.delete(
            f"/api/v1/devices/{default_devices[1].id}",
            headers=admin_headers,
        )
        assert response.status_code == 204

        # Try to get the deleted device
        response = client.get(
            f"/api/v1/devices/{default_devices[1].id}",
            headers=admin_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_devices(
        self, client: TestClient, admin_headers: dict, default_devices: list[Device]
    ):
        """Getting devices should return pre-populated default devices."""
        response = client.get("/api/v1/devices/", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

        device_names = [device.get("name", "") for device in data]
        assert "Test Device 2" in device_names

    @pytest.mark.asyncio
    async def test_read_device_not_found(self, client: TestClient):
        """Getting a non-existent device should return 404."""
        uid = UUID("00000000-0000-0000-0000-000000000000")
        response = client.get(f"/api/v1/devices/{uid}")
        assert response.status_code == 404
