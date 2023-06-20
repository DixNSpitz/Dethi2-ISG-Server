from flask import Blueprint

bp = Blueprint('auth', __name__)

from isg_api.auth import routes
