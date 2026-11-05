from datetime import timedelta 
import os

class Config:
   SECRET_KEY = os.environ.get("SECRET_KEY", None)

   REDIS_URL = "redis://localhost:6379/" # redis url which is important to create redis connection
   MAX_CONNECTIONS = 20 # REDIS max_connection value

   PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    
   # TODO: при необходимости добавить MAX_CONTENT_LENGTH, если буду реализовывать логику с загрузкой файлов
   SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///shop.db")
