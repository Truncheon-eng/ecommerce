from flask import Blueprint

bp = Blueprint(
    "cart",
    __name__
)

from . import routes
