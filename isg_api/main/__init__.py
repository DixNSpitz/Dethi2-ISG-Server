from flask import Blueprint
from flask_cors import CORS

bp = Blueprint('main', __name__)
CORS(bp)

from isg_api.main import routes
