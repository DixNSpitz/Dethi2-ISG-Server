from flask import redirect, render_template, request, flash, url_for, jsonify, abort
from flask_login import current_user, login_required

from isg_api.main import bp
from isg_api.globals import db
from isg_api.main.forms import SettingsForm
from isg_api.models import SensorData, SmartLeaf

import datetime
import statistics

from .game_state import GameState
import asyncio, struct
from bleak import BleakClient


address = "E8:9F:6D:22:7C:BE"

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
        date_list = [base_dt - datetime.timedelta(days=x) for x in range(7)]  # last 7 days

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
            mean_luminosity = None if not d_data_luminosity else statistics.mean(
                (d_d.value for d_d in d_data_luminosity))
            mean_temperature = None if not d_data_temperature else statistics.mean(
                (d_d.value for d_d in d_data_temperature))

            day_dict = {"id": i, "name": d.strftime("%A"), "water_value": mean_humidity, "light_value": mean_luminosity,
                        "temperature_value": mean_temperature}

            day_arr.append(day_dict)
            i += 1

        vital_dict["days"] = day_arr
        vital_arr.append(vital_dict)

    return jsonify(vital_arr)


game_state = GameState()
valid_games = ["humidity", "multiple", "order"]


@bp.route('/games', methods=['GET', 'POST'])
def game():
    try:
        request_data = request.get_json(silent=True)
        print(f"Method: {request.method}, JSON: {request_data}")  # Debugging line

        if request.method == 'POST':
            if request_data is None or 'game' not in request_data:
                abort(400, description="Missing 'game' key in request. The key 'game' is required.")

            game_to_start = request_data['game'].lower()
            print(f"Game to start: {game_to_start}")  # Debugging line

            if game_to_start == 'off':
                print("Attempting to stop game")  # Debugging line
                game_state.stop_game()
                print("Game stopped")  # Debugging line
            elif game_to_start not in valid_games:
                abort(400, description=f"Invalid game '{game_to_start}'. Available games are: {', '.join(valid_games)} or off")
            else:
                game_state.start_game(game_to_start)

            return jsonify({'message': 'Game updated'}), 200

        elif request.method == 'GET':
            return jsonify(game_state.get_state()), 200

        else:
            return jsonify({'message': 'Invalid HTTP method'}), 405

    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500

last_value = None

@bp.route('/light')
# login not required
async def light():   #bluetooth verbinden  
    global last_value
    async with BleakClient(address) as client:
        for service in client.services:
            if service.handle == 19:   
                for charact in service.characteristics:
                    if charact.handle == 20:
                        await client.start_notify(charact.uuid, notification_handler)
                        await asyncio.sleep(10) # 3 hours for tech-probe
                        await client.stop_notify(charact.uuid)
    return str(last_value), 200

def notification_handler(sender, data):
    global last_value
    #winsound.PlaySound("server/sounds/jump.wav", winsound.SND_FILENAME)
    last_value = struct.unpack('<i', data)[0]
    print('light_value:', last_value)
    print('notification handler is doing something')
    


