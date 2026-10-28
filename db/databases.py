import os

from dotenv import load_dotenv

load_dotenv()

DATABASES = {"ERP": "DB1", "TMS": "DB2", "kactus": "DB3"}


def get_database_settings(database: str) -> dict[str, str]:
    """Return the configured connection settings for a named database."""
    database_name = database.strip().casefold()
    aliases = {name.casefold(): name for name in DATABASES}
    if database_name not in aliases:
        available = ", ".join(DATABASES)
        raise ValueError(
            f"Base de datos desconocida: {database!r}. Opciones disponibles: {available}."
        )

    canonical_name = aliases[database_name]
    prefix = DATABASES[canonical_name]
    setting_names = {
        "server": f"{prefix}_SERVER",
        "database": f"{prefix}_DATABASE",
        "user": f"{prefix}_USER",
        "password": f"{prefix}_PASSWORD",
    }
    missing = [name for name in setting_names.values() if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            f"Faltan variables de configuración para {canonical_name}: "
            + ", ".join(missing)
        )

    return {key: os.environ[name] for key, name in setting_names.items()}
