PG_NAME = "analysis_db"
PG_USER = "furher"
PG_PASSWORD = "123gr"
PG_ADAPTER = "postgresql+asyncpg"
PG_HOST = "127.0.0.1"
PG_PORT = 5432
PG_SYNC_ADAPTER = "postgresql+psycopg2"


def get_connection_string(sync: bool = False) -> str:
    if sync:
        return (
            f"{PG_SYNC_ADAPTER}://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_NAME}"
        )
    return f"{PG_ADAPTER}://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_NAME}"


AMQP_USERNAME = "guest"
AMQP_PASSWORD = "custompassword123"
AMQP_HOST = "127.0.0.1"
AMQP_PORT = "5672"
AMQP_VIRTUALHOST = "/"
AMQP_QUEUE = "tasks"
