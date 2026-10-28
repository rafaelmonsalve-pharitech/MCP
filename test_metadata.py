import unittest
from unittest.mock import MagicMock, patch

from db.connection import get_connection
from tools.metadata import listar_tablas

from tools.query import ejecutar_select


def make_fake_connection():
    connection = MagicMock()
    cursor = (
        connection.__enter__.return_value.cursor.return_value.__enter__.return_value
    )
    cursor.fetchall.return_value = [{"TABLE_NAME": "example"}]
    return connection, cursor


class MetadataTests(unittest.TestCase):
    def test_lists_tables_without_leaking_the_connection(self):
        connection, cursor = make_fake_connection()
        with patch("tools.metadata.get_connection", return_value=connection):
            result = listar_tablas()

        self.assertEqual(result, [{"TABLE_NAME": "example"}])
        self.assertIn("INFORMATION_SCHEMA.TABLES", cursor.execute.call_args.args[0])


class QueryTests(unittest.TestCase):
    def test_executes_select_and_ignores_keywords_in_strings_and_comments(self):
        connection, cursor = make_fake_connection()
        query = "SELECT 'drop; delete' AS note -- update\n"

        with patch("tools.query.get_connection", return_value=connection):
            result = ejecutar_select(query)

        self.assertEqual(result, [{"TABLE_NAME": "example"}])
        cursor.execute.assert_called_once_with(query)

    def test_rejects_non_select_without_opening_a_connection(self):
        with patch("tools.query.get_connection") as get_connection:
            with self.assertRaisesRegex(ValueError, "Solo se permiten"):
                ejecutar_select("DELETE FROM users")

        get_connection.assert_not_called()

    def test_rejects_multiple_statements_without_opening_a_connection(self):
        with patch("tools.query.get_connection") as get_connection:
            with self.assertRaisesRegex(ValueError, "varias sentencias"):
                ejecutar_select("SELECT 1; DROP TABLE users")

        get_connection.assert_not_called()

    def test_rejects_write_cte_without_opening_a_connection(self):
        with patch("tools.query.get_connection") as get_connection:
            with self.assertRaisesRegex(ValueError, "DELETE"):
                ejecutar_select("WITH rows AS (SELECT 1) DELETE FROM users")

        get_connection.assert_not_called()


class ConnectionTests(unittest.TestCase):
    def test_reports_missing_connection_settings_without_connecting(self):
        with patch.dict("os.environ", {}, clear=True):
            with patch("db.connection.pytds.connect") as connect:
                with self.assertRaisesRegex(RuntimeError, "SQL_SERVER"):
                    get_connection()

        connect.assert_not_called()


if __name__ == "__main__":
    unittest.main()