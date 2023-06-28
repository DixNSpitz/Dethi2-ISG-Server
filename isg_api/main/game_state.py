from random import randrange
from isg_api.main.game_one_logic import choose_question, user_chose_plant, callback_touch
from isg_api.globals_smart_leafs import ble_smart_leafs

valid_games = ["humidity", "multiple", "order"]


class _GameState:
    def __init__(self):
        self.state = 'off'
        self.game = None

    def start_game(self, game):
        not_connected = False
        if ble_smart_leafs is None or len(ble_smart_leafs) == 0: not_connected = True
        for sl in ble_smart_leafs:
            if not sl.client.is_connected:
                not_connected = True

        #if not_connected:
        #    print('One or more Smart-Leafs are not conencted. Cannot start game!')
        #    return

        #rand_question_idx = randrange(1, 17)
        #correct_plant_id = choose_question(rand_question_idx)
        #if correct_plant_id < 0:
        #    return

        #def game_one_callback(client, value):
        #    chosen_plant_id = callback_touch(client, value)
        #    user_chose_plant(chosen_plant_id, correct_plant_id)
        #    self.stop_game()

        #for sl in ble_smart_leafs:
        #    sl.custom_callback_touch = game_one_callback
        #    sl.use_custom_callbacks = True

        if self.state == 'on':
            print(f"Stopping {self.game}")
        self.state = 'on'
        self.game = game
        print(f"Starting {game}")

    def stop_game(self):
        if self.state == 'on':
            print(f"Stopping {self.game}")
        self.state = 'off'
        self.game = None

        for sl in ble_smart_leafs:
            sl.custom_callback_touch = None
            sl.use_custom_callbacks = False


    def get_state(self):
        return {'state': self.state, 'game': self.game}


game_state = _GameState()
