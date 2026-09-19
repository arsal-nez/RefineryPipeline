import unittest
from unittest.mock import patch

from app import app


class ApiValidationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_chat_rejects_empty_body(self):
        response = self.client.post(
            "/api/chat",
            json={}
        )

        self.assertEqual(response.status_code, 400)

        data = response.get_json()

        self.assertFalse(data["success"])

    def test_chat_rejects_non_string_question(self):
        response = self.client.post(
            "/api/chat",
            json={"question": 123}
        )

        self.assertEqual(response.status_code, 400)

        data = response.get_json()

        self.assertFalse(data["success"])

    def test_chat_rejects_empty_question(self):
        response = self.client.post(
            "/api/chat",
            json={"question": "   "}
        )

        self.assertEqual(response.status_code, 400)

    def test_upload_requires_file(self):
        response = self.client.post(
            "/api/upload-blueprint",
            data={}
        )

        self.assertEqual(response.status_code, 400)

        data = response.get_json()

        self.assertFalse(data["success"])


if __name__ == "__main__":
    unittest.main()
