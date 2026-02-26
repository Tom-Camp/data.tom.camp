import pytest
from fastapi.testclient import TestClient

from app.models.device import Device


class TestData:

    @pytest.mark.asyncio
    async def test_add_data(
        self, client: TestClient, admin_headers: dict, default_devices: list
    ):
        """Adding data should return 201 and the data."""
        api_keys = client.post(
            f"/api/v1/keys/{default_devices[0].id}",
            headers=admin_headers,
        )
        data_headers: dict = {
            "X-API-Key": api_keys.json().get("api_key"),
            "X-Device-Id": str(default_devices[0].id),
        }
        response = client.post(
            "/api/v1/data/",
            json={"data": {"temperature": 25.5}},
            headers=data_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data.get("status", "") == "ok"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_add_data_bad_key(
        self, client: TestClient, admin_headers: dict, default_devices: list
    ):
        """Adding data should return 403."""
        data_headers: dict = {
            "X-API-Key": "00000000-0000-0000-0000-000000000000",
            "X-Device-Id": str(default_devices[0].id),
        }
        response = client.post(
            "/api/v1/data/",
            json={"data": {"temperature": 25.5}},
            headers=data_headers,
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_read_device_data(self, client: TestClient, device_with_data: Device):
        response = client.get(
            f"/api/v1/data/device/{device_with_data.id}",
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
