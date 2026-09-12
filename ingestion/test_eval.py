"""Tests d'évaluation de la recherche sémantique (RAG) et de pertinence des citations."""

import unittest
from fastapi.testclient import TestClient
from api.main import app


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_search_relevance_and_citations(self):
        response = self.client.get("/search?query=path%20parameters&library=fastapi&limit=3")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data["query"], "path parameters")
        results = data["results"]
        self.assertIsInstance(results, list)
        
        if len(results) > 0:
            top_result = results[0]
            self.assertIn("score", top_result)
            self.assertIn("content", top_result)
            self.assertIn("citation", top_result)
            
            citation = top_result["citation"]
            self.assertEqual(citation["library"], "fastapi")
            self.assertIsNotNone(citation["path"])
            self.assertIsNotNone(citation["commit"])
            self.assertIsNotNone(citation["url"])
            self.assertTrue(citation["url"].startswith("https://github.com/fastapi/fastapi/blob/"))


if __name__ == "__main__":
    unittest.main()
