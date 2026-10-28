from db.connection import get_connection


_PROHIBITED_KEYWORDS = {
    "ALTER",
    "BACKUP",
    "BULK",
    "CREATE",
    "DBCC",
    "DELETE",
    "DENY",
    "DROP",
    "EXEC",
    "EXECUTE",
    "GRANT",
    "INSERT",
    "INTO",
    "MERGE",
    "RESTORE",
    "REVOKE",
    "TRUNCATE",
    "UPDATE",
}


def _sql_tokens(query: str) -> list[str]:
    tokens = []
    index = 0

    while index < len(query):
        char = query[index]

        if char.isspace():
            index += 1
            continue

        if query.startswith("--", index):
            newline = query.find("\n", index + 2)
            index = len(query) if newline == -1 else newline + 1
            continue

        if query.startswith("/*", index):
            index += 2
            depth = 1
            while index < len(query) and depth:
                if query.startswith("/*", index):
                    depth += 1
                    index += 2
                elif query.startswith("*/", index):
                    depth -= 1
                    index += 2
                else:
                    index += 1
            if depth:
                raise ValueError("Comentario SQL sin cerrar.")
            continue

        if char == "'":
            index += 1
            while index < len(query):
                if query[index] == "'":
                    if index + 1 < len(query) and query[index + 1] == "'":
                        index += 2
                    else:
                        index += 1
                        break
                else:
                    index += 1
            else:
                raise ValueError("Cadena SQL sin cerrar.")
            continue

        if char in {'"', "["}:
            closing_char = "]" if char == "[" else '"'
            index += 1
            while index < len(query):
                if query[index] == closing_char:
                    if index + 1 < len(query) and query[index + 1] == closing_char:
                        index += 2
                    else:
                        index += 1
                        break
                else:
                    index += 1
            else:
                raise ValueError("Identificador SQL entrecomillado sin cerrar.")
            tokens.append("<quoted-identifier>")
            continue

        if char == ";":
            tokens.append(char)
            index += 1
            continue

        if char.isalpha() or char in "_@#":
            start = index
            index += 1
            while index < len(query) and (
                query[index].isalnum() or query[index] in "_@$#"
            ):
                index += 1
            tokens.append(query[start:index].upper())
            continue

        tokens.append(char)
        index += 1

    return tokens


def _validate_select_query(query: str) -> None:
    if not isinstance(query, str) or not query.strip():
        raise ValueError("La consulta debe ser una cadena SQL no vacía.")

    tokens = _sql_tokens(query)
    if not tokens or tokens[0] not in {"SELECT", "WITH"}:
        raise ValueError("Solo se permiten consultas SELECT.")

    if ";" in tokens:
        raise ValueError("No se permiten varias sentencias SQL.")

    prohibited = _PROHIBITED_KEYWORDS.intersection(tokens)
    if prohibited:
        keyword = sorted(prohibited)[0]
        raise ValueError(f"Comando no permitido: {keyword}")


def ejecutar_select(
    database: str,
    query: str,
):
    """Ejecuta SELECT de solo lectura en ERP, TMS o kactus."""
    _validate_select_query(query)

    conn = get_connection(database)
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
    finally:
        conn.close()