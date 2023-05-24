from flask import render_template
from isg_api import globals
from isg_api.errors import bp


# TODO do we need html templates => the webapp should probably handle error rendering
@bp.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@bp.errorhandler(500)
def internal_error(error):
    globals.db.session.rollback()
    return render_template('errors/500.html'), 500