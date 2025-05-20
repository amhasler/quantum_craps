import numpy as np
from src.agents.classical_agent import ClassicalAgent
from src.agents.quantum_agent import QuantumAgent
from src.agents.qbist_agent import QBistAgent
from src.agents.random_agent import RandomAgent
from src.simulator.payouts import PAYOUT_TABLE

# Example outcome probabilities and flat bets (adjust if needed)
OUTCOME_PROBS = {'win': 0.4929, 'lose': 0.5071}
FLAT_BETS = ['pass_line_flat', 'come_flat']

def dry_run():
    rng = np.random.default_rng(seed=42)
    num_games = 10

    agents = {
        "Classical": ClassicalAgent(
            payout_table=PAYOUT_TABLE,
            outcome_probs=OUTCOME_PROBS,
            flat_bets=FLAT_BETS,
            starting_bankroll=1000,
            table_minimum=10),
        "Quantum": QuantumAgent(
            max_combo_size=3,
            max_dim=6,
            starting_bankroll=1000,
            table_minimum=10),
        "QBist": QBistAgent(
            max_combo_size=3,
            max_dim=4,
            starting_bankroll=1000,
            table_minimum=10),
        "Random": RandomAgent(
            max_combo_size=3,
            starting_bankroll=1000,
            table_minimum=10)
    }

    from src.simulator.simulator import simulate_agent

    for name, agent in agents.items():
        bankroll_history = simulate_agent(agent, rng, num_games)
        print(f"{name} agent final bankroll after {num_games} games: ${bankroll_history[-1]:.2f}")
        print(f"{name} bankroll history: {bankroll_history}")

if __name__ == "__main__":
    dry_run()
