from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_wtf.csrf import CSRFProtect

from redis import Redis

import atexit 

def init_redis(app: Flask) -> None:
    """Должна быть вызвана внутри create_app"""
    app.extensions["redis_client"] = Redis.from_url(
        app.config["REDIS_URL"],
        max_connections=app.config["MAX_CONNECTIONS"] # остальные параметры оставим по умолчанию
    )

    # необходимо для удаления pool-а соединений
    atexit.register(app.extensions["redis_client"].close)
    return

def get_redis() -> Redis:
    return current_app.extensions["redis_client"]

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
csrf = CSRFProtect()
