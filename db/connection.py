import os

import pytds
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    required_settings = ("SQL_SERVER", "SQL_DATABASE", "SQL_USER", "SQL_PASSWORD")
    missing_settings = [name for name in required_settings if not os.getenv(name)]
    if missing_settings:
        raise RuntimeError(
            "Faltan variables de configuración: " + ", ".join(missing_settings)
        )

    return pytds.connect(
        server=os.environ["SQL_SERVER"],
        database=os.environ["SQL_DATABASE"],
        user=os.environ["SQL_USER"],
        password=os.environ["SQL_PASSWORD"],
        as_dict=True
    )