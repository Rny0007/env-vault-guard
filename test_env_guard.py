"""
Unit tests for Env Vault Guard.
"""

import unittest
import tempfile
import os
from env_guard import parse_env_file, audit_env


class TestEnvGuard(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def create_file(self, filename: str, content: str) -> str:
        path = os.path.join(self.tmp_dir.name, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def test_parse_env_file(self):
        content = (
            "# Database Settings\n"
            "DB_HOST=127.0.0.1\n"
            "DB_PORT=5432 # standard port\n"
            "API_KEY=\"secret_quoted_123\"\n"
            "\n"
            "EMPTY_VAR=\n"
        )
        fpath = self.create_file(".env", content)
        parsed = parse_env_file(fpath)
        self.assertEqual(parsed["DB_HOST"], "127.0.0.1")
        self.assertEqual(parsed["DB_PORT"], "5432")
        self.assertEqual(parsed["API_KEY"], "secret_quoted_123")
        self.assertEqual(parsed["EMPTY_VAR"], "")

    def test_audit_env_matching(self):
        tmpl = self.create_file(".env.example", "PORT=8080\nSECRET=your_key_here\n")
        actual = self.create_file(".env", "PORT=3000\nSECRET=prod_secret_abc\n")
        res = audit_env(tmpl, actual)
        self.assertTrue(res["passed"])
        self.assertEqual(len(res["missing_keys"]), 0)

    def test_audit_env_missing_keys(self):
        tmpl = self.create_file(".env.example", "PORT=8080\nDATABASE_URL=\nAPI_KEY=\n")
        actual = self.create_file(".env", "PORT=8080\n")
        res = audit_env(tmpl, actual)
        self.assertFalse(res["passed"])
        self.assertEqual(res["missing_keys"], ["API_KEY", "DATABASE_URL"])


if __name__ == "__main__":
    unittest.main()
