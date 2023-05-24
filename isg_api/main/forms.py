from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, ValidationError, EqualTo

from isg_api.models import User


class SettingsForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    password2 = PasswordField('Passwort wiederholen', validators=[DataRequired(), EqualTo('password')])
    password3 = PasswordField('Neues Passwort', validators=[DataRequired()])

    submit = SubmitField('Speichern')

    def __init__(self, original_username, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')
