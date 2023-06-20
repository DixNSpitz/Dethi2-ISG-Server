class GameState:
    def __init__(self):
        self.state = 'off'
        self.game = None

    def start_game(self, game):
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

    def get_state(self):
        return {'state': self.state, 'game': self.game}
