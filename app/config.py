import os

class Config:
   SECRET_KEY = os.environ.get("SECRET_KEY", None) 
   # при необходимости добавить MAX_CONTENT_LENGTH, если буду реализовывать логику с загрузкой файлов
   SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///shop.db")
