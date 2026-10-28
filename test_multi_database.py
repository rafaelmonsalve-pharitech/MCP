import asyncio
import os
import unittest
from unittest.mock import MagicMock, patch

from db.databases import get_database_settings
from db.connection import get_connection
from tools.metadata import listar_tablas
from tools.monitoring import health_check
from tools.procedures import listar_procedimientos
from tools.query import ejecutar_select


def fake_connection(rows=None, row=None):
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = rows or []
    cursor.fetchone.return_value = row
    return connection, cursor


class DatabaseSettingsTests(unittest.TestCase):
    def test_selects_settings_for_named_database(self):
        env = {
            "DB2_SERVER": "test-server",
            "DB2_DATABASE": "test-database",
            "DB2_USER": "test-user",
            "DB2_PASSWORD": "test-password",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = get_database_settings("TMS")

        self.assertEqual(
            settings,
            {
                "server": "test-server",
                "database": "test-database",
                "user": "test-user",
                "password": "test-password",
            },
        )

    def test_rejects_unknown_database(self):
        with self.assertRaisesRegex(ValueError, "Base de datos desconocida"):
            get_database_settings("unknown")

    def test_reports_missing_settings_without_connecting(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "DB1_SERVER"):
                get_connection("ERP")

    def test_connects_to_requested_database(self):
        env = {
            "DB3_SERVER": "test-server",
            "DB3_DATABASE": "test-database",
            "DB3_USER": "test-user",
            "DB3_PASSWORD": "test-password",
        }
        with patch.dict(os.environ, env, clear=True):
            with patch("db.connection.pytds.connect") as connect:
                get_connection("kactus")

        connect.assert_called_once_with(
            server="test-server",
            database="test-database",
            user="test-user",
            password="test-password",
            as_dict=True,
        )

    def test_tms_alias_is_case_insensitive(self):
        env = {
            "DB2_SERVER": "test-server",
            "DB2_DATABASE": "test-database",
            "DB2_USER": "test-user",
            "DB2_PASSWORD": "test-password",
        }
        with patch.dict(os.environ, env, clear=True):
            uppercase_settings = get_database_settings("TMS")
            lowercase_settings = get_database_settings("tms")

        self.assertEqual(uppercase_settings, lowercase_settings)


class DatabaseToolTests(unittest.TestCase):
    def test_select_returns_rows_and_closes_connection(self):
        connection, cursor = fake_connection(rows=[{"id": 1}])
        with patch("tools.query.get_connection", return_value=connection):
            result = ejecutar_select("ERP", "SELECT 1 AS id")

        self.assertEqual(result, [{"id": 1}])
        cursor.execute.assert_called_once_with("SELECT 1 AS id")
        connection.close.assert_called_once()

    def test_select_rejects_write_without_connecting(self):
        with patch("tools.query.get_connection") as connect:
            with self.assertRaisesRegex(ValueError, "Solo se permiten"):
                ejecutar_select("ERP", "DELETE FROM example")

        connect.assert_not_called()

    def test_metadata_uses_selected_database_and_closes_connection(self):
        connection, cursor = fake_connection(rows=[{"TABLE_NAME": "example"}])
        with patch("tools.metadata.get_connection", return_value=connection) as connect:
            result = listar_tablas("TMS")

        connect.assert_called_once_with("TMS")
        self.assertEqual(result, [{"TABLE_NAME": "example"}])
        connection.close.assert_called_once()
        self.assertIn("INFORMATION_SCHEMA.TABLES", cursor.execute.call_args.args[0])

    def test_health_check_uses_selected_database_and_closes_connection(self):
        connection, cursor = fake_connection(row={"servidor": "test-server"})
        with patch(
            "tools.monitoring.get_connection", return_value=connection
        ) as connect:
            result = health_check("kactus")

        connect.assert_called_once_with("kactus")
        self.assertEqual(result, {"servidor": "test-server"})
        connection.close.assert_called_once()
        cursor.execute.assert_called_once_with("SELECT @@SERVERNAME servidor")

    def test_lists_procedures_and_closes_connection(self):
        connection, cursor = fake_connection(rows=[{"ROUTINE_NAME": "example"}])
        with patch(
            "tools.procedures.get_connection", return_value=connection
        ) as connect:
            result = listar_procedimientos("ERP")

        connect.assert_called_once_with("ERP")
        self.assertEqual(result, [{"ROUTINE_NAME": "example"}])
        connection.close.assert_called_once()
        self.assertIn("sys.procedures", cursor.execute.call_args.args[0])

    def test_server_registers_all_database_tools(self):
        import server

        tools = asyncio.run(server.mcp.list_tools())
        self.assertEqual(
            {tool.name for tool in tools},
            {
                "ejecutar_select",
                "health_check",
                "listar_procedimientos",
                "listar_tablas",
            },
        )


if __name__ == "__main__":
    unittest.main()
