from db.connection import get_connection


def listar_procedimientos(database: str):
    """Lista procedimientos de ERP, TMS o kactus."""

    conn = get_connection(database)

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    SCHEMA_NAME(schema_id) AS ROUTINE_SCHEMA,
                    name AS ROUTINE_NAME
                FROM sys.procedures
                ORDER BY ROUTINE_SCHEMA, ROUTINE_NAME
            """)
            return cursor.fetchall()
    finally:
        conn.close()