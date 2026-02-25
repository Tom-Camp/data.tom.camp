import pytest


class TestMain:

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """The root endpoint should return 200."""
        response = client.get("/")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_read_item_not_found(self, client):
        """Requesting a non-existent ID should return 404."""
        response = client.get("/items/9999")
        assert response.status_code == 404
