import json
from src.simulator.simulator import Simulator


# This is all placeholder until I have a working json and simulator agents
class DummyAgent:
    def play_round(self, bankroll):
        bet_amount = 10
        bankroll -= bet_amount
        return bankroll

# Load parameters
def load_config(config_path='src/simulator/config.json'):
    with open(config_path, 'r') as file:
        config = json.load(file)
    return config


def main():
    # Load simulation parameters
    config = load_config()

    starting_bankroll = config.get('starting_bankroll', 1000)
    n_games = config.get('n_games', 1000)

    # Instantiate a dummy agent (placeholder)
    agent = DummyAgent()

    # Create the simulator
    simulator = Simulator(agent, starting_bankroll, n_games)

    # Run the simulation
    bankroll_history = simulator.run()

    # Print final bankroll
    final_bankroll = bankroll_history[-1]
    print(f"Final bankroll after {n_games} games: ${final_bankroll}")


if __name__ == "__main__":
    main()
