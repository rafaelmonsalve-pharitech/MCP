import pytds

from db.databases import get_database_settings


def get_connection(database: str):
    """Open a connection to one of the configured SQL Server databases."""
    settings = get_database_settings(database)
    return pytds.connect(**settings, as_dict=True)