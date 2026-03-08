from fastapi.testclient import TestClient

from app.models.device import Device


class TestData:

    def test_add_data(
        self, client: TestClient, admin_headers: dict, default_devices: list[Device]
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

    def test_add_data_bad_key(self, client: TestClient, default_devices: list):
        """Adding data with an invalid API key should return 401."""
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

    def test_add_data_missing_headers(self, client: TestClient):
        """Posting data without auth headers should return 401."""
        response = client.post("/api/v1/data/", json={"temperature": 25.5})
        assert response.status_code == 401

    def test_add_data_with_revoked_key(
        self, client: TestClient, admin_headers: dict, default_devices: list[Device]
    ):
        """Posting data with a revoked API key should return 401."""
        create_response = client.post(
            f"/api/v1/keys/{default_devices[0].id}",
            headers=admin_headers,
        )
        raw_key = create_response.json().get("api_key")
        client.patch(
            f"/api/v1/keys/{default_devices[0].id}/revoke",
            headers=admin_headers,
        )
        response = client.post(
            "/api/v1/data/",
            json={"temperature": 25.5},
            headers={
                "X-API-Key": raw_key,
                "X-Device-Id": str(default_devices[0].id),
            },
        )
        assert response.status_code == 401

    def test_read_device_data(self, client: TestClient, device_with_data: Device):
        response = client.get(
            f"/api/v1/data/device/{device_with_data.id}",
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

    def test_read_data_by_id(self, client: TestClient, device_with_data: Device):
        """Fetching a single data entry by ID should return 200 and the entry."""
        list_response = client.get(f"/api/v1/data/device/{device_with_data.id}")
        first_id = list_response.json()[0]["id"]

        response = client.get(f"/api/v1/data/{first_id}")
        assert response.status_code == 200
        assert response.json()["id"] == first_id

    def test_read_data_by_id_not_found(self, client: TestClient):
        """Fetching a non-existent data entry should return 404."""
        response = client.get("/api/v1/data/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    def test_data_list_pagination(self, client: TestClient, device_with_data: Device):
        """skip and limit should correctly page results."""
        all_response = client.get(f"/api/v1/data/device/{device_with_data.id}")
        all_ids = [entry["id"] for entry in all_response.json()]

        response = client.get(
            f"/api/v1/data/device/{device_with_data.id}",
            params={"skip": 1, "limit": 1},
        )
        assert response.status_code == 200
        page = response.json()
        assert len(page) == 1
        assert page[0]["id"] == all_ids[1]

    def test_data_list_order(self, client: TestClient, device_with_data: Device):
        """Both asc and desc order parameters are accepted and return all records."""
        desc_response = client.get(
            f"/api/v1/data/device/{device_with_data.id}",
            params={"order": "desc"},
        )
        asc_response = client.get(
            f"/api/v1/data/device/{device_with_data.id}",
            params={"order": "asc"},
        )
        assert desc_response.status_code == 200
        assert asc_response.status_code == 200
        assert len(desc_response.json()) == 3
        assert len(asc_response.json()) == 3
