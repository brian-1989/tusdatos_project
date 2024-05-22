from datetime import timedelta
import secrets
import os

POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "oOvoiZizblnksdOWPiNYWzHfMrlTEJIM"
POSTGRES_HOST = "roundhouse.proxy.rlwy.net"
POSTGRES_PORT = "13760"
POSTGRES_DB = "railway"

secret_key = secrets.token_hex(32)

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', "postgresql://{}:{}@{}:{}/{}".format(
        POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = secret_key
    JWT_SECRET_KEY = secret_key
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_ALGORITHM = "HS256"
