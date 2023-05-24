from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
login = LoginManager()
migrate = Migrate()
bootstrap = Bootstrap5()

login.login_view = 'auth.login'
login.login_message = 'Bitte einloggen um diese Seite anzuzeigen'
login.needs_refresh_message = 'Bitte erneut einloggen'
