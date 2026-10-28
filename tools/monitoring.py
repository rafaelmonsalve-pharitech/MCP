from db.connection import get_connection


def health_check(database: str):
    """Comprueba ERP, TMS o kactus e informa el servidor SQL."""

    conn = get_connection(database)

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT @@SERVERNAME servidor")
            return cursor.fetchone()
    finally:
        conn.close()