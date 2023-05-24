from flask import Blueprint

bp = Blueprint('main', __name__)

from isg_api.main import routes
