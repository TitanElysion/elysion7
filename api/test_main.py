from fastapi.testclient import TestClient
import unittest

from api.main import app


class APITests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("collection", data)

    def test_search_no_collection(self):
        # Without indexed collection, search should return 503 or handle gracefully
        response = self.client.get("/search?query=fastapi")
        self.assertIn(response.status_code, [503, 200])


if __name__ == "__main__":
    unittest.main()
