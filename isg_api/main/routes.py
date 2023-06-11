from flask import redirect, render_template, request, flash, url_for, jsonify
from flask_login import current_user, login_required

from isg_api.main import bp
from isg_api.globals import db
from isg_api.main.forms import SettingsForm
from isg_api.models import SensorData, SmartLeaf

import datetime
import statistics

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
    vital_arr = []

    leafs = SmartLeaf.query.all()
    for leaf in leafs:
        vital_dict = {"id": leaf.id, "name": leaf.plant.name, "days": []}
        day_arr = []

        base_dt = datetime.date.today()
        date_list = [base_dt - datetime.timedelta(days=x) for x in range(7)] # last 7 days

        i = 1
        for d in date_list:
            d_data = [d_d for d_d in leaf.data if d_d.measured_on.date() == d]
            d_data_luminosity = [d_d for d_d in d_data if d_d.sensor_type_id == 1]
            d_data_humidity = [d_d for d_d in d_data if d_d.sensor_type_id == 2]
            d_data_temperature = SensorData.query.filter(
                SensorData.sensor_type_id == 3,
                SensorData.measured_on >= d.strftime('%Y-%m-%d'),
                SensorData.measured_on < (d + datetime.timedelta(days=1)).strftime('%Y-%m-%d')).all()

            mean_humidity = None if not d_data_humidity else statistics.mean((d_d.value for d_d in d_data_humidity))
            mean_luminosity = None if not d_data_luminosity else statistics.mean((d_d.value for d_d in d_data_luminosity))
            mean_temperature = None if not d_data_temperature else statistics.mean((d_d.value for d_d in d_data_temperature))

            day_dict = {"id": i, "name": d.strftime("%A"), "water_value": mean_humidity, "light_value": mean_luminosity, "temperature_value": mean_temperature}

            day_arr.append(day_dict)
            i += 1

        vital_dict["days"] = day_arr
        vital_arr.append(vital_dict)

    return jsonify(vital_arr)

    # mocked_vitals = [
    #     {"id": "1",
    #      "name": "Tomate",
    #      "days": [
    #          {
    #              "id": "1",
    #              "name": "Montag",
    #              "water_value": 0.5,
    #              "light_value": 2000.5,
    #              "temperature_value": 23,
    #          }, {
    #              "id": "2",
    #              "name": "Dienstag",
    #              "water_value": 0.5,
    #              "light_value": 2000.5,
    #              "temperature_value": 23,
    #          }, {
    #              "id": "3",
    #              "name": "Mittwoch",
    #              "water_value": 0.5,
    #              "light_value": 2000.5,
    #              "temperature_value": 23,
    #          }, {
    #              "id": "4",
    #              "name": "Donnerstag",
    #              "water_value": 0.5,
    #              "light_value": 2000.5,
    #              "temperature_value": 23,
    #          }, {
    #              "id": "5",
    #              "name": "Freitag",
    #              "water_value": 0.5,
    #              "light_value": 2000.5,
    #              "temperature_value": 23,
    #          }, {
    #              "id": "6",
    #              "name": "Samstag",
    #              "water_value": 0.5,
    #              "light_value": 2000.5,
    #              "temperature_value": 23,
    #          }, {
    #              "id": "7",
    #              "name": "Sonntag",
    #              "water_value": 0.5,
    #              "light_value": 2000.5,
    #              "temperature_value": 23,
    #          },
    #      ]
    #      },
    #     {"id": "2",
    #      "name": "Chili",
    #      "days": [
    #          {
    #              "id": "1",
    #              "name": "Montag",
    #              "water_value": 0.5,
    #              "light_value": 2000.5,
    #              "temperature_value": 23,
    #          }, {
    #              "id": "2",
    #              "name": "Dienstag",
    #              "water_value": 0.5,
    #              "light_value": 2000.5,
    #              "temperature_value": 23,
    #          }, {
    #              "id": "3",
    #              "name": "Mittwoch",
    #              "water_value": 0.5,
    #              "light_value": 2000.5,
    #              "temperature_value": 23,
    #          }, {
    #              "id": "4",
    #              "name": "Donnerstag",
    #              "water_value": 0.5,
    #              "light_value": 2000.5,
    #              "temperature_value": 23,
    #          }, {
    #              "id": "5",
    #              "name": "Freitag",
    #              "water_value": 0.5,
    #              "light_value": 2000.5,
    #              "temperature_value": 23,
    #          }, {
    #              "id": "6",
    #              "name": "Samstag",
    #              "water_value": 0.5,
    #              "light_value": 2000.5,
    #              "temperature_value": 23,
    #          }, {
    #              "id": "7",
    #              "name": "Sonntag",
    #              "water_value": 0.5,
    #              "light_value": 2000.5,
    #              "temperature_value": 23,
    #          },
    #      ]
    #      },
    #     {"id": "3",
    #      "name": "Aloe Vera",
    #      "days": [
    #          {
    #              "id": "1",
    #              "name": "Montag",
    #              "water_value": 0.5,
    #              "light_value": 2000.5,
    #              "temperature_value": 23,
    #          }, {
    #              "id": "2",
    #              "name": "Dienstag",
    #              "water_value": 0.5,
    #              "light_value": 2000.5,
    #              "temperature_value": 23,
    #          }, {
    #              "id": "3",
    #              "name": "Mittwoch",
    #              "water_value": 0.5,
    #              "light_value": 2000.5,
    #              "temperature_value": 23,
    #          }, {
    #              "id": "4",
    #              "name": "Donnerstag",
    #              "water_value": 0.5,
    #              "light_value": 2000.5,
    #              "temperature_value": 23,
    #          }, {
    #              "id": "5",
    #              "name": "Freitag",
    #              "water_value": 0.5,
    #              "light_value": 2000.5,
    #              "temperature_value": 23,
    #          }, {
    #              "id": "6",
    #              "name": "Samstag",
    #              "water_value": 0.5,
    #              "light_value": 2000.5,
    #              "temperature_value": 23,
    #          }, {
    #              "id": "7",
    #              "name": "Sonntag",
    #              "water_value": 0.5,
    #              "light_value": 2000.5,
    #              "temperature_value": 23,
    #          },
    #      ]
    #      },
    # ]
    # return jsonify(mocked_vitals)
