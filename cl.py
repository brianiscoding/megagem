class Player:
    def __init__(self, name):
        self.name = name
        self.is_alive = True  # or any relevant state

    def take_action(self, game_state):
        """Define what a player does on their turn."""
        action = input(f"{self.name}, enter your action: ")
        return action


class Game:
    def __init__(self, players):
        self.players = players
        self.current_turn = 0
        self.is_running = True
        self.state = {}  # any shared game state (board, score, etc.)

    def setup(self):
        """Initialize the game before the loop starts."""
        print("Game starting!")
        # e.g. deal cards, place pieces, randomize order, etc.

    def get_current_player(self):
        return self.players[self.current_turn % len(self.players)]

    def process_action(self, player, action):
        """Apply a player's action to the game state."""
        # validate and resolve the action
        pass

    def check_win_condition(self):
        """Return the winner if one exists, otherwise None."""
        # e.g. check if a player has 0 HP, reached a goal, etc.
        return None

    def end_turn(self):
        """Advance to the next turn."""
        self.current_turn += 1

    def display_state(self):
        """Show the current game state to players."""
        print(f"\n--- Turn {self.current_turn + 1} ---")
        print(f"State: {self.state}")

    def run(self):
        self.setup()

        while self.is_running:
            self.display_state()

            player = self.get_current_player()
            action = player.take_action(self.state)
            self.process_action(player, action)

            winner = self.check_win_condition()
            if winner:
                print(f"\n{winner.name} wins!")
                self.is_running = False
                break

            self.end_turn()

        self.on_game_over()

    def on_game_over(self):
        """Any cleanup or final output after the game ends."""
        print("Game over!")


# --- Entry point ---
if __name__ == "__main__":
    players = [Player("Alice"), Player("Bob")]
    game = Game(players)
    game.run()
