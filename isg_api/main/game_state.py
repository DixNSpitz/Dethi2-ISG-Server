import playsound
from flask import current_app
from random import randrange
from os import path
from isg_api.main.game_one_logic import choose_question, user_chose_plant


valid_games = ["humidity", "multiple", "order"]


class _GameState:
    def __init__(self):
        self.state = 'off'
        self.game = None

    def start_game(self, game):
        if self.state == 'on':
            print(f"Stopping {self.game}")
        self.state = 'on'
        self.game = game
        print(f"Starting {game}")
        rand_question_idx = randrange(1, 17)
        choose_question(rand_question_idx)


    def stop_game(self):
        if self.state == 'on':
            print(f"Stopping {self.game}")
        self.state = 'off'
        self.game = None

    def get_state(self):
        return {'state': self.state, 'game': self.game}


game_state = _GameState()
