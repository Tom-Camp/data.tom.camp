from uuid import UUID


class TestMain:

    def test_root_redirects(self, client):
        """The root endpoint should redirect to /docs."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307

    def test_device_not_found(self, client):
        """Requesting a non-existent device ID should return 404."""
        uid = UUID("00000000-0000-0000-0000-000000000000")
        response = client.get(f"/api/v1/devices/{uid}")
        assert response.status_code == 404
