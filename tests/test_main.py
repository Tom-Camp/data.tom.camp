class TestMain:

    def test_root_redirects(self, client):
        """The root endpoint should redirect to /docs."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307

    def test_health(self, client):
        """Health endpoint should return 200 with status ok."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
