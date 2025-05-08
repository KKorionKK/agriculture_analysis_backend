import os
from pathlib import Path
from dotenv import dotenv_values

environment = os.getenv("ENV")
env = dotenv_values(str(Path().absolute().parent) + "/.env")
print(str(Path().absolute().parent) + "/.env")

# PostgreSQL
PG_NAME = env.get("PG_NAME")
PG_USER = env.get("PG_USER")
PG_PASSWORD = env.get("PG_PASSWORD")
PG_ADAPTER = env.get("PG_ADAPTER")
PG_HOST = env.get("PG_HOST")
PG_PORT = int(env.get("PG_PORT"))
PG_SYNC_ADAPTER = env.get("PG_SYNC_ADAPTER")


def get_connection_string(sync: bool = False) -> str:
    if sync:
        return (
            f"{PG_SYNC_ADAPTER}://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_NAME}"
        )
    return f"{PG_ADAPTER}://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_NAME}"


# Security
ACCESS_SECURITY_TOKEN_EXPIRES = 24 * 60
REFRESH_SECURITY_TOKEN_EXPIRES = 24 * 60 * 7
SECRET = "99386269ab1b3ce9614a8f8d3c2ea27771bee1dab037ed1d069935c72c65903e"
ALGORITHM = "HS256"

# RabbitMQ
AMQP_USERNAME = env.get("AMQP_USERNAME")
AMQP_PASSWORD = env.get("AMQP_PASSWORD")
AMQP_HOST = env.get("AMQP_HOST")
AMQP_PORT = env.get("AMQP_PORT")
AMQP_VIRTUALHOST = env.get("AMQP_VIRTUALHOST")
AMQP_QUEUE = env.get("AMQP_QUEUE")

# S3 Storage
S3_ACCESS_ID = env.get("S3_ACCESS_ID")
S3_SECRET_KEY = env.get("S3_SECRET_KEY")
S3_BUCKET = env.get("S3_BUCKET")
