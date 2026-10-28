from db.connection import get_connection


def listar_tablas(database: str):
    """Lista tablas de usuario de ERP, TMS o kactus."""

    conn = get_connection(database)

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    TABLE_SCHEMA,
                    TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
            """)
            return cursor.fetchall()
    finally:
        conn.close()