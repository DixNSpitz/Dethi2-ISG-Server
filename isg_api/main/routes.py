from flask import redirect, render_template, request, flash, url_for, current_app, Markup
from flask_login import current_user, login_required

from isg_api.main import bp
from isg_api.globals import db
from isg_api.main.forms import SettingsForm


@bp.route('/')
@bp.route('/index')
def home():
    return render_template('index.html')


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.set_password(form.password3.data)
        db.session.commit()
        flash('Änderungen wurden gespeichert')
        return redirect(url_for('main.settings'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('settings.html', form=form) # TODO send just the form?, is it even needed with Webapp?