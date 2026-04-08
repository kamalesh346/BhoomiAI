from fastapi.testclient import TestClient
from main import app
import unittest
from unittest.mock import patch

client = TestClient(app)

class TestHealth(unittest.TestCase):
    @patch("api.routes.health._conn")
    @patch("api.routes.health.load_vectorstore")
    def test_health_check_healthy(self, mock_load_vectorstore, mock_conn):
        # Mocking DB connection
        mock_conn.return_value.cursor.return_value.execute.return_value = None
        
        # Mocking RAG vectorstore
        mock_load_vectorstore.return_value = True
        
        response = client.get("/health/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["components"]["api"], "ok")
        self.assertEqual(data["components"]["database"], "connected")
        self.assertEqual(data["components"]["rag"], "loaded")

    @patch("api.routes.health._conn")
    @patch("api.routes.health.load_vectorstore")
    def test_health_check_degraded(self, mock_load_vectorstore, mock_conn):
        # Mocking DB connection error
        mock_conn.side_effect = Exception("DB Connection Error")
        
        # Mocking RAG vectorstore
        mock_load_vectorstore.return_value = None
        
        response = client.get("/health/")
        self.assertEqual(response.status_code, 200) # Should still return 200 but with degraded status
        data = response.json()
        self.assertEqual(data["status"], "degraded")
        self.assertTrue("error" in data["components"]["database"])
        self.assertEqual(data["components"]["rag"], "failed to load")

if __name__ == "__main__":
    unittest.main()
