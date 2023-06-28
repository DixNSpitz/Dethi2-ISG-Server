from playsound import playsound
from flask import current_app
from os import path
from isg_api.models import SmartLeaf

# key: Frage-Idx, Value: Tuple (Frage-Sound-File, correct plant-id for answer)
_sound_files = {
    1: ("frage1.wav", 2),
    2: ("frage2.wav", 3),
    3: ("frage3.wav", 1),
    4: ("frage4.wav", 3),
    5: ("frage5.wav", 2),
    6: ("frage6.wav", 1),
    7: ("frage7.wav", 3),
    8: ("frage8.wav", 2),
    9: ("frage9.wav", 3),
    10: ("frage10.wav", 2),
    11: ("frage11.wav", 1),
    12: ("frage12.wav", 3),
    13: ("frage13.wav", 1),
    14: ("frage14.wav", 1),
    15: ("frage15.wav", 3),
    16: ("frage16.wav", 1),
}

# Sound files for answers
_sound_files_answers = {
    "tomato": {
        "right": "richtig_tomate.wav",
        "wrong": "falsch_tomate.wav"
    },
    "chili": {
        "right": "richtig_chili.wav",
        "wrong": "falsch_chili.wav"
    },
    "aloevera": {
        "right": "richtig_aloevera.wav",
        "wrong": "falsch_aloevera.wav"
    }
}

# Map index to plant name
_index_to_plant = {
    1: "tomato",
    2: "chili",
    3: "aloevera"
}


def callback_touch(client, value):
    with current_app.app_context():
        sl = SmartLeaf.query.filter(SmartLeaf.mac_address == client.address).first()
        if sl and sl.plant:
            return sl.plant.id

    return -1


# Tomate: 1 # Chili: 2 # Aloe Vera: 3
# Pick random sound file
def choose_question(q_idx):
    if q_idx in _sound_files:
        p = path.join(current_app.root_path, 'static', 'sounds', _sound_files[q_idx][0])
        try:
            playsound(p)
        except Exception as e:
            print('Error while trying to play sound-file:', p, 'Msg:', e)
            return None

        # Return correct plant-idx
        return _index_to_plant[_sound_files[q_idx][1]]
    else:
        print(f"Invalid sound value: {q_idx}")
        return None


def user_chose_plant(user_chosen_plant_id, correct_plant_id):
    current_plant = _index_to_plant.get(user_chosen_plant_id, None)
    answer_correct = user_chosen_plant_id == correct_plant_id

    if current_plant:
        if answer_correct:
            sound_file = _sound_files_answers[current_plant]["right"]
        else:
            sound_file = _sound_files_answers[current_plant]["wrong"]

        # Play the sound
        p = path.join(current_app.root_path, 'static', 'sounds', sound_file)
        try:
            playsound(p)

        except Exception as e:
            print('Error while trying to play sound-file:', p, 'Msg:', e)
        print(f'Sound played: {sound_file}')

    else:
        print(f"Invalid plant index: {user_chosen_plant_id}")
