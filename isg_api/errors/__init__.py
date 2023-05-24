from flask import Blueprint

bp = Blueprint('errors', __name__)

from isg_api.errors import handlers
