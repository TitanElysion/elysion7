import unittest

from ingestion.chunker import split_text
from ingestion.indexer import point_id, source_url
from ingestion.pipeline import classify_path


class IngestionTests(unittest.TestCase):
    def test_long_text_is_split(self):
        chunks = split_text("word " * 400, chunk_size=1200, overlap=150)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(80 <= len(chunk) <= 1200 for chunk in chunks))

    def test_source_url_uses_immutable_commit(self):
        chunk = {
            "repository": "https://github.com/fastapi/fastapi.git",
            "commit": "abc123",
            "path": "docs/index.md",
        }
        self.assertEqual(
            source_url(chunk),
            "https://github.com/fastapi/fastapi/blob/abc123/docs/index.md",
        )

    def test_point_ids_are_stable(self):
        chunk = {"library": "fastapi", "commit": "abc", "path": "a.py", "section": None, "chunk_index": 0, "content": "hello"}
        self.assertEqual(point_id(chunk), point_id(chunk))

    def test_path_classification(self):
        self.assertEqual(classify_path("docs/tutorial.md"), "documentation")
        self.assertEqual(classify_path("fastapi/routing.py"), "source")


if __name__ == "__main__":
    unittest.main()
