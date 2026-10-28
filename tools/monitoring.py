from db.connection import get_connection


def health_check():
    """Comprueba la conexión y devuelve el nombre del servidor SQL."""

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT @@SERVERNAME servidor")
            return cursor.fetchone()