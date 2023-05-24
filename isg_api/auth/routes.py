from flask import request, flash, render_template, url_for, redirect
from flask_login import current_user, login_user, logout_user

from werkzeug.urls import url_parse

from isg_api.models import User
from isg_api.auth import bp
from isg_api.auth.forms import LoginForm


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.settings'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Inkorrekter Username oder Passwort', 'error')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.settings')
        return redirect(next_page)
    return render_template('auth/login.html', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))