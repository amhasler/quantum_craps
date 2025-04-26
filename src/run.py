import sys
import os
import json

# Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from simulator.simulator import Simulator

# Placeholder until json working
class DummyAgent:
    def play_round(self, bankroll):

        bet_amount = 10
        bankroll -= bet_amount
        return bankroll


def load_config():
    # More robust call to json file
    base_dir = os.path.dirname(__file__)  # This gets the directory where run.py is
    config_path = os.path.join(base_dir, 'simulator', 'config.json')

    with open(config_path, 'r') as file:
        config = json.load(file)

    return config


def main():
    # Load simulation settings
    config = load_config()

    starting_bankroll = config.get('starting_bankroll', 1000)
    n_games = config.get('n_games', 1000)

    # Instantiate a dummy agent
    agent = DummyAgent()

    # Create and run the simulator
    simulator = Simulator(agent, starting_bankroll, n_games)
    bankroll_history = simulator.run()

    # Output final results
    final_bankroll = bankroll_history[-1]
    print(f"Final bankroll after {n_games} games: ${final_bankroll}")


if __name__ == "__main__":
    main()

