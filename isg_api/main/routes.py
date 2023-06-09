from flask import redirect, render_template, request, flash, url_for, jsonify
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
    return render_template('settings.html', form=form)  # TODO send just the form?, is it even needed with Webapp?


@bp.route('/vitals')
# login not required
def vitals():
    mocked_vitals = [
        {"id": "1",
         "name": "Tomate",
         "days": [
             {
                 "id": "1",
                 "name": "Montag",
                 "water_value": 0.5,
                 "light_value": 2000.5,
                 "temperature_value": 23,
             }, {
                 "id": "2",
                 "name": "Dienstag",
                 "water_value": 0.5,
                 "light_value": 2000.5,
                 "temperature_value": 23,
             }, {
                 "id": "3",
                 "name": "Mittwoch",
                 "water_value": 0.5,
                 "light_value": 2000.5,
                 "temperature_value": 23,
             }, {
                 "id": "4",
                 "name": "Donnerstag",
                 "water_value": 0.5,
                 "light_value": 2000.5,
                 "temperature_value": 23,
             }, {
                 "id": "5",
                 "name": "Freitag",
                 "water_value": 0.5,
                 "light_value": 2000.5,
                 "temperature_value": 23,
             }, {
                 "id": "6",
                 "name": "Samstag",
                 "water_value": 0.5,
                 "light_value": 2000.5,
                 "temperature_value": 23,
             }, {
                 "id": "7",
                 "name": "Sonntag",
                 "water_value": 0.5,
                 "light_value": 2000.5,
                 "temperature_value": 23,
             },
         ]
         },
        {"id": "2",
         "name": "Chili",
         "days": [
             {
                 "id": "1",
                 "name": "Montag",
                 "water_value": 0.5,
                 "light_value": 2000.5,
                 "temperature_value": 23,
             }, {
                 "id": "2",
                 "name": "Dienstag",
                 "water_value": 0.5,
                 "light_value": 2000.5,
                 "temperature_value": 23,
             }, {
                 "id": "3",
                 "name": "Mittwoch",
                 "water_value": 0.5,
                 "light_value": 2000.5,
                 "temperature_value": 23,
             }, {
                 "id": "4",
                 "name": "Donnerstag",
                 "water_value": 0.5,
                 "light_value": 2000.5,
                 "temperature_value": 23,
             }, {
                 "id": "5",
                 "name": "Freitag",
                 "water_value": 0.5,
                 "light_value": 2000.5,
                 "temperature_value": 23,
             }, {
                 "id": "6",
                 "name": "Samstag",
                 "water_value": 0.5,
                 "light_value": 2000.5,
                 "temperature_value": 23,
             }, {
                 "id": "7",
                 "name": "Sonntag",
                 "water_value": 0.5,
                 "light_value": 2000.5,
                 "temperature_value": 23,
             },
         ]
         },
        {"id": "3",
         "name": "Aloe Vera",
         "days": [
             {
                 "id": "1",
                 "name": "Montag",
                 "water_value": 0.5,
                 "light_value": 2000.5,
                 "temperature_value": 23,
             }, {
                 "id": "2",
                 "name": "Dienstag",
                 "water_value": 0.5,
                 "light_value": 2000.5,
                 "temperature_value": 23,
             }, {
                 "id": "3",
                 "name": "Mittwoch",
                 "water_value": 0.5,
                 "light_value": 2000.5,
                 "temperature_value": 23,
             }, {
                 "id": "4",
                 "name": "Donnerstag",
                 "water_value": 0.5,
                 "light_value": 2000.5,
                 "temperature_value": 23,
             }, {
                 "id": "5",
                 "name": "Freitag",
                 "water_value": 0.5,
                 "light_value": 2000.5,
                 "temperature_value": 23,
             }, {
                 "id": "6",
                 "name": "Samstag",
                 "water_value": 0.5,
                 "light_value": 2000.5,
                 "temperature_value": 23,
             }, {
                 "id": "7",
                 "name": "Sonntag",
                 "water_value": 0.5,
                 "light_value": 2000.5,
                 "temperature_value": 23,
             },
         ]
         },
    ]
    return jsonify(mocked_vitals)
