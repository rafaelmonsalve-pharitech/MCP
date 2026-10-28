from db.connection import get_connection


def listar_tablas():
    """Lista las tablas de usuario disponibles en la base de datos configurada."""

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
            """)
            return cursor.fetchall()